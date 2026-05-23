import frappe
import re
from frappe.model.document import Document
from frappe import _

class VendorRegistration(Document):
    
    def autoname(self):
        """Generate naming series based on source"""
        if self.source == 'Nafed(Manual)':
            # For manual entries, use naming series
            self.name = frappe.model.naming.make_autoname('VR-XXXX.#####', self)
        else:
            # For other sources, use timestamp-based naming
            self.name = f"VR-{frappe.utils.now_datetime().strftime('%Y%m%d%H%M%S')}"
    
    def validate(self):
        self.validate_formats()
        self.validate_duplicates()
        self.validate_conditional_fields()
        self.check_blacklist()
        self.set_defaults()
        
        # Auto-create vendor code for non-Nafed sources
        non_nafed_sources = ['E-samridhi', 'E-pravha', 'E-auction', 'Other']
        if self.source in non_nafed_sources and not self.vendor_code:
            self.generate_vendor_code()
    
    def on_update(self):
        """Handle post-save operations"""
        non_nafed_sources = ['E-samridhi', 'E-pravha', 'E-auction', 'Other']
        
        # For non-Nafed sources, auto-create supplier after save
        if self.source in non_nafed_sources and self.vendor_code:
            if not frappe.db.exists('Supplier', {'supplier_name': self.vendor_code}):
                self.create_erpnext_supplier()
                self.send_welcome_email()
                
                # Update workflow state to Active (bypassing workflow)
                self.db_set('workflow_state', 'Active', update_modified=False)
                self.db_set('docstatus', 1, update_modified=False)
                
                frappe.msgprint(
                    f'Vendor Registration completed. Vendor Code: {self.vendor_code}',
                    indicator='green'
                )
    
    def on_submit(self):
        """
        For Nafed(Manual) source: triggered when document is submitted via workflow
        """
        if self.source == 'Nafed(Manual)':
            # Only generate if not already exists
            if not self.vendor_code:
                self.generate_vendor_code()
            
            # Create supplier if doesn't exist
            if not frappe.db.exists('Supplier', {'supplier_name': self.vendor_code}):
                self.create_erpnext_supplier()
                self.send_welcome_email()
            
            self.set_isd_approved_flag()
    
    def before_cancel(self):
        """Handle cancellation - disable supplier if exists"""
        if self.vendor_code and frappe.db.exists('Supplier', {'supplier_name': self.vendor_code}):
            frappe.db.set_value('Supplier', {'supplier_name': self.vendor_code}, 'disabled', 1)
    
    # ═══════════════════════════════════════════════════════════
    # VALIDATE METHODS
    # ═══════════════════════════════════════════════════════════

    def set_defaults(self):
        if not self.get('registration_date'):
            self.registration_date = frappe.utils.today()

    def validate_formats(self):
        if self.pan:
            if not re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$', self.pan.upper()):
                frappe.throw(f'Invalid PAN format: {self.pan}. Expected: ABCDE1234F')
            self.pan = self.pan.upper()
        if self.gstin:
            if not re.match(
                r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$',
                self.gstin.upper()
            ):
                frappe.throw(f'Invalid GSTIN format: {self.gstin}. Must be 15 characters.')
            self.gstin = self.gstin.upper()
        if self.ifsc_code:
            if not re.match(r'^[A-Z]{4}0[A-Z0-9]{6}$', self.ifsc_code.upper()):
                frappe.throw(f'Invalid IFSC: {self.ifsc_code}. Example: HDFC0001234')
            self.ifsc_code = self.ifsc_code.upper()
        if self.mobile_number:
            if not re.match(r'^[6-9][0-9]{9}$', str(self.mobile_number)):
                frappe.throw(f'Invalid mobile: {self.mobile_number}. Must be 10 digits starting 6-9')

    def validate_duplicates(self):
        checks = [
            ('pan',           self.pan,           'PAN'),
            ('gstin',         self.gstin,         'GSTIN'),
            ('mobile_number', self.mobile_number, 'Mobile Number'),
            ('email_id',      self.email_id,      'Email ID'),
        ]
        for field, value, label in checks:
            if not value:
                continue
            existing = frappe.db.get_value(
                'Vendor Registration',
                {field: value, 'name': ['!=', self.name]},
                'name'
            )
            if existing:
                frappe.throw(
                    f'Duplicate {label}: {value} already exists '
                    f'in registration {existing}.'
                )

    def validate_conditional_fields(self):
        if self.get('msme_registered') and not self.get('msme_number'):
            frappe.throw('MSME Number is required when MSME Registered is ticked')
        if self.get('fssai_required') and not self.get('fssai_number'):
            frappe.throw('FSSAI Number is required when FSSAI Required is ticked')
        if self.get('classification') == 'Rejected' and not self.get('rejection_reason'):
            frappe.throw('Rejection Reason is mandatory when Classification is Rejected')

    def check_blacklist(self):
        if not self.pan and not self.gstin:
            return
        result = frappe.db.sql("""
            SELECT name, blacklist_reason FROM `tabVendor Registration`
            WHERE (pan = %(pan)s OR gstin = %(gstin)s)
            AND blacklisted = 1 AND name != %(current)s
        """, {'pan': self.pan or '', 'gstin': self.gstin or '', 'current': self.name}, as_dict=True)
        if result:
            frappe.throw(
                f'This vendor is BLACKLISTED. Reason: {result[0].blacklist_reason}. '
                f'Registration blocked. Contact HO Admin.'
            )

    # ═══════════════════════════════════════════════════════════
    # VENDOR CODE + SUPPLIER CREATION
    # ═══════════════════════════════════════════════════════════

    def generate_vendor_code(self):
        if self.vendor_code:
            return self.vendor_code
            
        cat_map = {
            'Supplier': 'SUP', 'Transporter': 'TRN', 'Miller': 'MIL',
            'Surveyor': 'SRV', 'Service Provider': 'SVC',
        }
        state_map = {
            'Maharashtra': 'MH', 'Delhi': 'DL', 'Karnataka': 'KA',
            'Tamil Nadu': 'TN', 'Gujarat': 'GJ', 'Rajasthan': 'RJ',
            'Uttar Pradesh': 'UP', 'Punjab': 'PB', 'Haryana': 'HR',
            'Madhya Pradesh': 'MP', 'West Bengal': 'WB',
            'Andhra Pradesh': 'AP', 'Telangana': 'TG', 'Kerala': 'KL',
        }
        
        cat_code = cat_map.get(self.vendor_category, 'GEN')
        state_code = state_map.get(self.state, 'XX')
        
        # Get the last sequence number for this combination
        last = frappe.db.sql("""
            SELECT vendor_code FROM `tabVendor Registration`
            WHERE vendor_code LIKE %(pattern)s
            ORDER BY vendor_code DESC LIMIT 1
        """, {'pattern': f'VND-{state_code}-{cat_code}-%'}, as_dict=True)
        
        seq = 1
        if last and last[0].get('vendor_code'):
            try:
                last_seq = int(last[0]['vendor_code'].split('-')[-1])
                seq = last_seq + 1
            except (ValueError, IndexError, AttributeError):
                seq = 1
        
        # Generate unique vendor code
        vendor_code = f'VND-{state_code}-{cat_code}-{seq:04d}'
        
        # Ensure uniqueness
        while frappe.db.exists('Vendor Registration', {'vendor_code': vendor_code}):
            seq += 1
            vendor_code = f'VND-{state_code}-{cat_code}-{seq:04d}'
        
        self.vendor_code = vendor_code
        return self.vendor_code

    def create_erpnext_supplier(self):
        if not self.vendor_code:
            frappe.log_error('vendor_code empty', 'Vendor Registration')
            return
            
        # Check if supplier already exists
        existing = frappe.db.get_value('Supplier', {'supplier_name': self.vendor_code}, 'name')
        if existing:
            frappe.msgprint(f'Supplier already exists: {existing}', indicator='blue')
            return
            
        # Get company and account details
        company = (
            frappe.defaults.get_user_default('Company') or
            frappe.db.get_single_value('Global Defaults', 'default_company')
        )
        
        ap_account = None
        if company:
            ap_account = frappe.db.get_value('Company', company, 'default_payable_account')
        
        # Prepare supplier document
        supplier_doc = {
            'doctype': 'Supplier',
            'supplier_name': self.vendor_code,
            'supplier_group': self.vendor_category or 'All Supplier Groups',
            'supplier_type': 'Company',  # or 'Individual' based on your requirement
            'country': 'India',
            'pan': self.pan,
            'gstin': self.gstin,
            'custom_vendor_type': self.vendor_category,
            'custom_vendor_registration': self.name,  # Link back to registration
            'custom_isd_approved': 1 if self.get('isd_approved') else 0,
            'custom_blacklisted': 0,
            'disabled': 0,  # Enable by default
        }
        
        # Add bank details if available
        if self.get('bank_name') and self.get('bank_account_no'):
            supplier_doc['custom_bank_name'] = self.bank_name
            supplier_doc['custom_bank_account'] = self.bank_account_no
            supplier_doc['custom_ifsc_code'] = self.ifsc_code
        
        # Add accounting entries
        if company and ap_account:
            supplier_doc['accounts'] = [{
                'doctype': 'Party Account',
                'company': company,
                'account': ap_account,
            }]
        
        try:
            supplier = frappe.get_doc(supplier_doc)
            supplier.flags.ignore_permissions = True
            supplier.flags.ignore_mandatory = True
            supplier.insert(ignore_permissions=True)
            
            frappe.db.commit()
            
            frappe.msgprint(
                f'Supplier {self.vendor_code} created successfully.',
                indicator='green'
            )
            
        except Exception as e:
            frappe.log_error(f"Supplier creation failed: {str(e)}", "Vendor Registration")
            frappe.msgprint(
                f'Warning: Supplier creation failed. Please create manually. Error: {str(e)}',
                indicator='orange'
            )

    def send_welcome_email(self):
        if not self.email_id or not self.vendor_code:
            return
            
        try:
            frappe.sendmail(
                recipients=[self.email_id],
                subject=f'NAFED — Vendor Registration Approved | {self.vendor_code}',
                message=f"""Dear {self.vendor_name},

Your vendor registration with NAFED has been approved.

Vendor Code : {self.vendor_code}
Category    : {self.vendor_category}
Source      : {self.source}

You can now log in to the NAFED Vendor Portal.

Regards,
NAFED ERP Team"""
            )
        except Exception as e:
            frappe.log_error(f"Email sending failed: {str(e)}", "Vendor Registration")

    def set_isd_approved_flag(self):
        divisions = self.get('approved_divisions') or []
        if 'ISD' in divisions:
            frappe.db.set_value('Vendor Registration', self.name, 'isd_approved', 1)


# ── Standalone hook function for workflow state changes ──────
def on_update_after_submit(doc, method=None):
    """
    Handle workflow state changes for Nafed(Manual) source only
    """
    # Only process for Nafed(Manual) source
    if doc.source != 'Nafed(Manual)':
        return
        
    state = doc.workflow_state
    
    if state == 'Branch Reviewed':
        # Notify HO Procurement Officers
        ho_users = frappe.get_all('Has Role',
            filters={'role': 'HO Procurement Officer', 'parenttype': 'User'},
            pluck='parent')
        
        if ho_users:
            frappe.sendmail(
                recipients=ho_users,
                subject=f'Vendor Pending HO Approval — {doc.vendor_name}',
                message=f"""
                Vendor {doc.vendor_name} ({doc.name}) has been reviewed by branch.
                
                Registration ID: {doc.name}
                Vendor Category: {doc.vendor_category}
                State: {doc.state}
                
                Please review and take necessary action.
                """
            )
    
    elif state == 'HO Approved':
        # Generate vendor code
        if not doc.vendor_code:
            vendor_code = doc.generate_vendor_code()
            doc.db_set('vendor_code', vendor_code, update_modified=False)

            # Send vendor notification immediately after code generation
            doc.send_welcome_email()

        # Create supplier and ensure vendor gets final confirmation
        if not frappe.db.exists('Supplier', {'supplier_name': doc.vendor_code}):
            doc.create_erpnext_supplier()

        # Enable supplier if disabled
        if doc.vendor_code and frappe.db.exists('Supplier', {'supplier_name': doc.vendor_code}):
            frappe.db.set_value('Supplier', {'supplier_name': doc.vendor_code}, 'disabled', 0)
    
    elif state == 'Rejected':
        # Notify vendor
        if doc.email_id:
            frappe.sendmail(
                recipients=[doc.email_id],
                subject='NAFED — Vendor Registration Status Update',
                message=f"""
                Dear {doc.vendor_name},
                
                Your registration has been reviewed and was not approved at this time.
                
                Reason: {doc.get('rejection_reason') or 'Please contact NAFED for more information.'}
                
                You may resubmit your application after making the necessary corrections.
                
                Regards,
                NAFED ERP Team
                """
            )
    
    elif state == 'Suspended':
        # Disable supplier
        if doc.vendor_code and frappe.db.exists('Supplier', {'supplier_name': doc.vendor_code}):
            frappe.db.set_value('Supplier', {'supplier_name': doc.vendor_code}, 'disabled', 1)
            frappe.db.commit()
    
    elif state == 'Active':
        # Enable supplier
        if doc.vendor_code and frappe.db.exists('Supplier', {'supplier_name': doc.vendor_code}):
            frappe.db.set_value('Supplier', {'supplier_name': doc.vendor_code}, 'disabled', 0)
            frappe.db.commit()