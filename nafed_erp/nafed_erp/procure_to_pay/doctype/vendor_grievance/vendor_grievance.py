import frappe
from frappe.model.document import Document
from frappe.utils import today, now_datetime, add_days, get_datetime
from frappe.utils import today

class VendorGrievance(Document):

    def validate(self):
        self.validate_vendor_registered()
        self.auto_fetch_vendor_name()
        self.set_sla_deadlines()
        self.validate_reopen_reason()
        self.set_defaults()

    def on_submit(self):
        self.set_submission_meta()
        self.send_acknowledgement_email()

    def on_update_after_submit(self):
        self.check_sla_breach()

        # State: Under Review
        if self.workflow_state == 'Under Review':
            self.set_assigned_officer()

        # State: Resolved — waiting for vendor response
        if self.workflow_state == 'Resolved':
            # Clear vendor_satisfaction so vendor can respond fresh
            self.db_set('vendor_satisfaction', None, update_modified=False)
            self.set_resolution_meta()
            self.notify_vendor_satisfaction_check()

        # State: Reopened — vendor not satisfied, escalate to HO
        if self.workflow_state == 'Reopened':
            # Set Not Satisfied only if not already set by vendor
            if self.vendor_satisfaction != 'Not Satisfied':
                self.db_set('vendor_satisfaction', 'Not Satisfied', update_modified=False)
                frappe.db.commit()
            self.notify_ho_on_reopen()

        # State: Closed — via Vendor Satisfied OR HO Close
        if self.workflow_state == 'Closed':
            # Always mark Satisfied on close — whether vendor closed
            # directly or HO resolved after reopen
            self.db_set('vendor_satisfaction', 'Satisfied', update_modified=False)
            frappe.db.commit()
            self.set_closed_meta()
            self.notify_vendor_closed()
            
    def set_defaults(self):
        if not self.grievance_id:  
           count = frappe.db.count('Vendor Grievance') + 1  
           self.grievance_id = f'GRV-{today().replace("-","")}-{count:04d}'        

    # ═══════════════════════════════════════════════════
    # VALIDATE METHODS
    # ═══════════════════════════════════════════════════

    def validate_vendor_registered(self):
        if not self.vendor_id:
            frappe.throw('Vendor ID is mandatory.')
        if not self.grievance_type:
            frappe.throw('Grievance Type is mandatory.')
        if not self.description:
            frappe.throw('Description is mandatory.')
        state = frappe.db.get_value(
            'Vendor Registration', self.vendor_id, 'workflow_state'
        )
        if not state:
            frappe.throw(f'Vendor {self.vendor_id} not found in system.')
        if state not in ('Active', 'HO Approved'):
            frappe.throw(
                f'Vendor {self.vendor_id} is not Active (status: {state}). '
                f'Only active vendors can submit grievances.'
            )

    def auto_fetch_vendor_name(self):
        if self.vendor_id and not self.vendor_name:
            self.vendor_name = frappe.db.get_value(
                'Vendor Registration', self.vendor_id, 'vendor_name'
            )

    def set_sla_deadlines(self):
        sla_days = {
            'Payment': 7, 'Purchase Order': 5,
            'Quality': 7, 'Tender': 10,
            'Portal': 3, 'Other': 7,
        }
        if not self.acknowledgement_deadline:
            self.acknowledgement_deadline = add_days(now_datetime(), 1)
        if not self.resolution_deadline:
            days = sla_days.get(self.grievance_type, 7)
            self.resolution_deadline = add_days(now_datetime(), days)

    def validate_reopen_reason(self):
        # Block Vendor Not Satisfied workflow if vendor has not provided reopen_reason
        user_roles = frappe.get_roles(frappe.session.user)
        if 'Vendor' in user_roles:
            if (self.workflow_state == 'Resolved'
                    and self.vendor_satisfaction == 'Not Satisfied'
                    and not self.reopen_reason):
                frappe.throw(
                    'Please fill in the <b>Reopen Reason</b> field and save '
                    'before selecting Not Satisfied.'
                )

    # ═══════════════════════════════════════════════════
    # ON SUBMIT METHODS
    # ═══════════════════════════════════════════════════

    def set_submission_meta(self):
        """
        Only db_set fields that actually exist in the DocType.
        Add submission_date and submitted_by fields via Customize Form
        if you want them stored. Until then, this is safe.
        """
        self._safe_db_set('submission_date', today())
        self._safe_db_set('submitted_by', frappe.session.user)

    def send_acknowledgement_email(self):
        vendor_email = frappe.db.get_value(
            'Vendor Registration', self.vendor_id, 'email_id'
        )
        if not vendor_email:
            return
        frappe.sendmail(
            recipients=[vendor_email],
            subject=f'Grievance Received — Reference: {self.name}',
            message=(
                f'Dear {self.vendor_name},\n\n'
                f'Your grievance has been received successfully.\n'
                f'Grievance ID : {self.name}\n'
                f'Type         : {self.grievance_type}\n'
                f'Status       : Submitted\n\n'
                f'Our Branch Manager will review and respond within '
                f'{self._get_sla_days()} working days.\n\n'
                f'You can track your grievance status by logging into the portal.'
            )
        )

    def _get_sla_days(self):
        sla_map = {
            'Payment': 7, 'Purchase Order': 5,
            'Quality': 7, 'Tender': 10,
            'Portal': 3, 'Other': 7,
        }
        return sla_map.get(self.grievance_type, 7)

    # ═══════════════════════════════════════════════════
    # ON UPDATE AFTER SUBMIT METHODS
    # ═══════════════════════════════════════════════════

    def set_assigned_officer(self):
        if not self.assigned_officer:
            self._safe_db_set('assigned_officer', frappe.session.user)

    def set_resolution_meta(self):
        self._safe_db_set('resolved_by', frappe.session.user)
        self._safe_db_set('resolution_date', today())

    def notify_vendor_satisfaction_check(self):
        vendor_email = frappe.db.get_value(
            'Vendor Registration', self.vendor_id, 'email_id'
        )
        if not vendor_email:
            return
        frappe.sendmail(
            recipients=[vendor_email],
            subject=f'Grievance Resolved — Action Required — {self.name}',
            message=(
                f'Dear {self.vendor_name},\n\n'
                f'Your grievance {self.name} has been reviewed and resolved '
                f'by our Branch Manager.\n\n'
                f'Resolution Type    : {self.resolution_type or "See details"}\n'
                f'Resolution Details : {self.resolution_details or "Please login to view"}\n\n'
                f'Please login to the NAFED portal and confirm:\n'
                f'  -> Click SATISFIED to close the grievance\n'
                f'  -> Click NOT SATISFIED to escalate to HO Division\n\n'
                f'Your response is required within 3 working days.'
            )
        )

    def notify_ho_on_reopen(self):
        ho_users = frappe.get_all(
            'Has Role',
            filters={'role': 'HO Admin'},
            pluck='parent'
        )
        if not ho_users:
            return
        frappe.sendmail(
            recipients=ho_users,
            subject=f'Vendor Not Satisfied — Grievance Reopened — {self.name}',
            message=(
                f'Vendor {self.vendor_name} is not satisfied with the '
                f'Branch Manager resolution of grievance {self.name}.\n\n'
                f'Grievance Type    : {self.grievance_type}\n'
                f'Vendor Reason     : {self.reopen_reason or "Not provided"}\n'
                f'Branch Resolution : {self.resolution_details or "Not recorded"}\n\n'
                f'Please login to ERP and provide HO response to close this.'
            )
        )

    def set_closed_meta(self):
        self._safe_db_set('ho_closed_by', frappe.session.user)
        self._safe_db_set('ho_closed_date', today())

    def notify_vendor_closed(self):
        vendor_email = frappe.db.get_value(
            'Vendor Registration', self.vendor_id, 'email_id'
        )
        if not vendor_email:
            return
        frappe.sendmail(
            recipients=[vendor_email],
            subject=f'Grievance Closed — {self.name}',
            message=(
                f'Dear {self.vendor_name},\n\n'
                f'Your grievance {self.name} has been closed.\n\n'
                f'Final Resolution : {self.ho_response or self.resolution_details}\n'
                f'Closed Date      : {today()}\n\n'
                f'Thank you for your patience. Please contact NAFED if you need further support.'
            )
        )

    def check_sla_breach(self):
        closed_states = ['Closed', 'Rejected / Invalid']
        if self.workflow_state in closed_states:
            return
        now = get_datetime(now_datetime())
        if (self.resolution_deadline
                and now > get_datetime(self.resolution_deadline)
                and self.sla_status != 'SLA Breached'):
            self._safe_db_set('sla_status', 'SLA Breached')
            self._alert_sla_breach()

    def _alert_sla_breach(self):
        ho_users = frappe.get_all(
            'Has Role', filters={'role': 'HO Admin'}, pluck='parent'
        )
        if ho_users:
            frappe.sendmail(
                recipients=ho_users,
                subject=f'SLA BREACH — Grievance {self.name}',
                message=(
                    f'Grievance {self.name} has exceeded its SLA deadline.\n'
                    f'Vendor   : {self.vendor_name}\n'
                    f'Type     : {self.grievance_type}\n'
                    f'Status   : {self.workflow_state}\n'
                    f'Deadline : {self.resolution_deadline}'
                )
            )

    def _safe_db_set(self, fieldname, value):
        """
        db_set only if the field actually exists in the DocType.
        Prevents OperationalError: Unknown column when fields are
        not yet added via Customize Form.
        """
        meta = frappe.get_meta('Vendor Grievance')
        if meta.has_field(fieldname):
            self.db_set(fieldname, value, update_modified=False)
        else:
            # Field not in DocType yet — skip silently
            frappe.log_error(
                f'VendorGrievance._safe_db_set: field "{fieldname}" not found in DocType. '
                f'Add it via Customize Form to persist this value.',
                'Missing Field Warning'
            )


# ── PERMISSION FILTER ─────────────────────────────────────────

def get_permission_query_conditions(user):
    if not user:
        user = frappe.session.user

    user_roles = frappe.get_roles(user)

    # System Manager / Administrator — sees everything including drafts
    if 'System Manager' in user_roles or 'Administrator' in user_roles:
        return ''

    # Branch Officer — sees all except Draft state
    if 'Branch Officer' in user_roles:
        return (
            "(`tabVendor Grievance`.`docstatus` = 1 OR "
            "`tabVendor Grievance`.`workflow_state` != 'Draft')"
        )

    # HO Admin — sees all except Draft state
    if 'HO Admin' in user_roles:
        return (
            "(`tabVendor Grievance`.`docstatus` = 1 OR "
            "`tabVendor Grievance`.`workflow_state` != 'Draft')"
        )

    # Vendor — sees only their own records (draft + submitted)
    vendor_id = frappe.db.get_value(
        'Vendor Registration',
        {'email_id': user},
        'name'
    )
    if vendor_id:
        return f"`tabVendor Grievance`.`vendor_id` = '{vendor_id}'"

    # Match by user field in Vendor Registration
    vendor_id_by_user = frappe.db.get_value(
        'Vendor Registration',
        {'user': user},
        'name'
    )
    if vendor_id_by_user:
        return f"`tabVendor Grievance`.`vendor_id` = '{vendor_id_by_user}'"

    # No match — block all access
    return "`tabVendor Grievance`.`name` = '__NO_ACCESS__'"

# ── DAILY SCHEDULER ───────────────────────────────────────────

def check_grievance_sla_breaches():
    open_grievances = frappe.get_all(
        'Vendor Grievance',
        filters={
            'docstatus': 1,
            'workflow_state': ['not in', ['Closed', 'Rejected / Invalid']],
        },
        pluck='name'
    )
    for name in open_grievances:
        doc = frappe.get_doc('Vendor Grievance', name)
        doc.check_sla_breach()
    frappe.db.commit()