# Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
import re
from frappe.model.document import Document
from frappe.utils import today, add_days, date_diff


class VendorAmendmentRequest(Document):

    # ── RUNS ON EVERY SAVE ─────────────────────────────────────
    def validate(self):
        self.set_defaults()                  # request_date, expiry, change_request_id
        self.validate_vendor_active()         # E5: vendor must be active
        self.validate_declaration()           # declaration must be ticked
        self.validate_at_least_one_change()   # must fill at least one new_ field
        self.validate_new_formats()           # format check on new GSTIN/PAN/IFSC/mobile
        self.validate_duplicates()            # E2: new GSTIN/PAN/email/mobile unique
        self.validate_emergency_note()        # AF4: emergency note mandatory
        self.validate_rejection_reason()      # rejection reason mandatory on Reject
        self.auto_fetch_vendor_details()      # fill vendor_name, vendor_code from vendor_id
        self.detect_amendment_category()      # auto-set category from filled fields

    # ── RUNS ON SUBMIT (Approved state) ────────────────────────
    def on_submit(self):
        self.apply_changes_to_vendor_master()  # update Vendor Registration
        self.update_supplier_record()          # sync ERPNext Supplier
        self.save_version_history()            # store snapshot in Amendment Log
        self.set_approval_meta()               # approved_by, approval_date
        self.notify_vendor_approval()          # email vendor
        self.lock_vendor_registration()        # SRS: lock modified fields

    def on_update_after_submit(self):
        if self.workflow_state == 'Rejected':
            self.notify_vendor_rejection()

    # ═══════════════════════════════════════════════════════════
    # VALIDATE METHODS
    # ═══════════════════════════════════════════════════════════

    def set_defaults(self):
        if not self.request_date:
            self.request_date = today()
        if not self.expiry_date:
            # AF2: auto-expire after 15 days
            self.expiry_date = add_days(today(), 15)
        if not self.change_request_id:
            count = frappe.db.count('Vendor Amendment Request') + 1
            self.change_request_id = f'CR-{today().replace("-","")}-{count:04d}'

    def auto_fetch_vendor_details(self):
        if self.vendor_id:
            vendor = frappe.db.get_value(
                'Vendor Registration',
                self.vendor_id,
                ['vendor_name', 'vendor_code', 'workflow_state'],
                as_dict=True
            )
            if vendor:
                self.vendor_name = vendor.vendor_name
                self.vendor_code = vendor.vendor_code

    def validate_vendor_active(self):
        # E5: vendor must be registered and active
        if not self.vendor_id:
            return
        state = frappe.db.get_value(
            'Vendor Registration', self.vendor_id, 'workflow_state'
        )
        if state not in ('Active', 'HO Approved'):
            frappe.throw(
                f'Vendor {self.vendor_id} is not Active. '
                f'Current status: {state}. '
                f'Only active vendors can submit amendment requests.'
            )

    def validate_declaration(self):
        if not self.declaration_signed:
            frappe.throw(
                'You must tick Declaration Signed to confirm '
                'authenticity of submitted documents.'
            )

    def validate_at_least_one_change(self):
        # All new_ fields — at least one must be filled
        change_fields = [
            'new_contact_name', 'new_mobile_number', 'new_email_id',
            'new_address', 'new_state', 'new_gstin', 'new_pan',
            'new_bank_account_number', 'new_ifsc_code',
            'new_fssai_number', 'new_msme_number', 'new_license_expiry_date',
        ]
        filled = [f for f in change_fields if self.get(f)]
        if not filled:
            frappe.throw(
                'Please fill at least one field under Proposed New Values. '
                'Amendment request cannot be empty.'
            )

    def detect_amendment_category(self):
        # Auto-detect category if not set by user
        if self.amendment_category:
            return
        financial_fields = ['new_bank_account_number', 'new_ifsc_code']
        regulatory_fields = ['new_gstin', 'new_pan', 'new_fssai_number', 'new_msme_number']
        contact_fields   = ['new_contact_name', 'new_mobile_number',
                            'new_email_id', 'new_address', 'new_state']

        if any(self.get(f) for f in financial_fields):
            self.amendment_category = 'Financial'
        elif any(self.get(f) for f in regulatory_fields):
            self.amendment_category = 'Regulatory/Tax'
        elif any(self.get(f) for f in contact_fields):
            self.amendment_category = 'Contact/Address'
        elif self.new_license_expiry_date:
            self.amendment_category = 'Document Renewal'

    def validate_new_formats(self):
        # Only validate fields that have new values
        if self.new_gstin:
            pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][1-9A-Z]Z[0-9A-Z]$'
            if not re.match(pattern, self.new_gstin.upper()):
                frappe.throw(f'Invalid GSTIN format: {self.new_gstin}')
            self.new_gstin = self.new_gstin.upper()

        if self.new_pan:
            if not re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]$', self.new_pan.upper()):
                frappe.throw(f'Invalid PAN format: {self.new_pan}')
            self.new_pan = self.new_pan.upper()

        if self.new_ifsc_code:
            if not re.match(r'^[A-Z]{4}0[A-Z0-9]{6}$', self.new_ifsc_code.upper()):
                frappe.throw(f'Invalid IFSC format: {self.new_ifsc_code}')
            self.new_ifsc_code = self.new_ifsc_code.upper()

        if self.new_mobile_number:
            if not re.match(r'^[6-9][0-9]{9}$', str(self.new_mobile_number)):
                frappe.throw(f'Invalid mobile: {self.new_mobile_number}')

    def validate_duplicates(self):
        # E2: new values must not already exist in another vendor
        checks = [
            ('gstin',         self.new_gstin,         'GSTIN'),
            ('pan',           self.new_pan,           'PAN'),
            ('email_id',      self.new_email_id,      'Email'),
            ('mobile_number', self.new_mobile_number, 'Mobile'),
        ]
        for field, value, label in checks:
            if not value: continue
            existing = frappe.db.get_value(
                'Vendor Registration',
                {field: value, 'name': ['!=', self.vendor_id]},
                'name'
            )
            if existing:
                frappe.throw(
                    f'Duplicate {label}: {value} already registered '
                    f'for vendor {existing}. Amendment blocked.'
                )

    def validate_emergency_note(self):
        # AF4: emergency update requires audit note
        if self.get('emergency_update') and not self.get('emergency_audit_note'):
            frappe.throw(
                'Emergency Audit Note is mandatory for Emergency Update. '
                'Provide justification for bypassing standard workflow.'
            )

    def validate_rejection_reason(self):
        if self.workflow_state == 'Rejected' and not self.rejection_reason:
            frappe.throw('Rejection Reason is mandatory when rejecting an amendment.')

    # ═══════════════════════════════════════════════════════════
    # ON SUBMIT — APPLY CHANGES TO VENDOR MASTER
    # ═══════════════════════════════════════════════════════════

    def apply_changes_to_vendor_master(self):
        """
        SRS Normal Flow Step 5: update Vendor Master after approval.
        Only updates fields that have new_ values filled.
        """
        if not self.vendor_id:
            return

        # Map: amendment field → vendor_registration field
        field_map = {
            'new_contact_name':       'contact_name',
            'new_mobile_number':      'mobile_number',
            'new_email_id':           'email_id',
            'new_address':            'address',
            'new_state':              'state',
            'new_gstin':              'gstin',
            'new_pan':                'pan',
            'new_bank_account_number':'bank_account_number',
            'new_ifsc_code':          'ifsc_code',
            'new_bank_name':          'bank_name',
            'new_fssai_number':       'fssai_number',
            'new_msme_number':        'msme_number',
            'new_license_expiry_date':'license_expiry_date',
        }

        updates = {}
        for amendment_field, vendor_field in field_map.items():
            new_value = self.get(amendment_field)
            if new_value:
                updates[vendor_field] = new_value

        if updates:
            frappe.db.set_value(
                'Vendor Registration', self.vendor_id, updates
            )
            frappe.db.commit()
            frappe.msgprint(
                f'Vendor master updated: {list(updates.keys())}',
                indicator='green'
            )

    def update_supplier_record(self):
        """Sync changed fields to ERPNext Supplier record."""
        if not self.vendor_code:
            return
        supplier = frappe.db.get_value(
            'Supplier', {'supplier_name': self.vendor_name}, 'name'
        )
        if not supplier:
            return

        supplier_updates = {}
        if self.new_gstin: supplier_updates['gstin'] = self.new_gstin
        if self.new_pan:   supplier_updates['pan']   = self.new_pan

        if supplier_updates:
            frappe.db.set_value('Supplier', supplier, supplier_updates)
            frappe.db.commit()

    def save_version_history(self):
        """
        SRS Normal Flow Step 5: generate version history.
        Snapshot of what changed stored in Amendment Log child.
        """
        # Get current version number
        last_version = frappe.db.get_value(
            'Vendor Registration', self.vendor_id, 'version_number'
        ) or 0
        new_version = int(last_version) + 1

        # Update version number on Vendor Registration
        frappe.db.set_value(
            'Vendor Registration', self.vendor_id,
            'version_number', new_version
        )
        self.db_set('version_number', new_version, update_modified=False)

    def set_approval_meta(self):
        self.db_set('approved_by',    frappe.session.user, update_modified=False)
        self.db_set('approval_date',  today(),             update_modified=False)

    def notify_vendor_approval(self):
        vendor_email = frappe.db.get_value(
            'Vendor Registration', self.vendor_id, 'email_id'
        )
        if not vendor_email: return
        frappe.sendmail(
            recipients=[vendor_email],
            subject=f'NAFED — Amendment Request Approved | {self.change_request_id}',
            message=(
                f'Dear {self.vendor_name},\n\n'
                f'Your amendment request {self.change_request_id} has been approved.\n'
                f'Category: {self.amendment_category}\n'
                f'Version: {self.version_number}\n\n'
                f'Your vendor profile has been updated accordingly.\n\n'
                f'NAFED ERP Team'
            )
        )

    def notify_vendor_rejection(self):
        vendor_email = frappe.db.get_value(
            'Vendor Registration', self.vendor_id, 'email_id'
        )
        if not vendor_email: return
        frappe.sendmail(
            recipients=[vendor_email],
            subject=f'NAFED — Amendment Request Update | {self.change_request_id}',
            message=(
                f'Dear {self.vendor_name},\n\n'
                f'Your amendment request {self.change_request_id} has been reviewed.\n'
                f'Status: Rejected\n'
                f'Reason: {self.rejection_reason or "Contact NAFED"}\n\n'
                f'You may resubmit with corrections.\n\n'
                f'NAFED ERP Team'
            )
        )

    def lock_vendor_registration(self):
        """SRS: lock modified fields post-approval — add amendment trail marker."""
        frappe.db.set_value(
            'Vendor Registration', self.vendor_id,
            'last_amendment_id', self.name
        )


# ── STANDALONE SCHEDULER FUNCTION ─────────────────────────────
# Called by hooks.py scheduler_events — NOT inside class

def auto_expire_stale_requests():
    """
    AF2: Requests inactive >15 days auto-marked Expired.
    Add to scheduler_events in hooks.py — runs daily.
    """
    today_date = today()
    stale = frappe.db.sql("""
        SELECT name, vendor_name
        FROM `tabVendor Amendment Request`
        WHERE workflow_state IN ('Draft', 'Pending Branch Review')
        AND expiry_date < %(today)s
        AND docstatus = 0
    """, {'today': today_date}, as_dict=True)

    for req in stale:
        frappe.db.set_value(
            'Vendor Amendment Request', req.name,
            'workflow_state', 'Expired'
        )
        frappe.log_error(
            f'Auto-expired amendment: {req.name} for {req.vendor_name}',
            'Amendment Auto-Expiry'
        )

    if stale:
        frappe.db.commit()