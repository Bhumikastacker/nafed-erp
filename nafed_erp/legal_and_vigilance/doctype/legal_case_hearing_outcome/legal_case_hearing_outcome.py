# Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
# For license information, please see license.txt


import frappe
from frappe.model.document import Document
from frappe.utils import now
from frappe.utils import getdate, today

class LegalCaseHearingOutcome(Document):
    
    def validate(self):

        # Hearing Date past me nahi honi chahiye
        if self.hearing_date and getdate(self.hearing_date) < getdate(today()):
            frappe.throw("Hearing Date cannot be in the past")

        # Next Hearing Date hearing date se chhoti nahi honi chahiye
        if self.hearing_date and self.next_hearing_date:
            if getdate(self.next_hearing_date) <= getdate(self.hearing_date):
                frappe.throw("Next Hearing Date must be future date")

    def before_insert(self):
        self.timeline_timestamp = now()
        self.created_by = frappe.session.user

        if self.awaiting_next_date:
            self.status = "Awaiting Next Date"
        else:
            self.status = "Saved"

    def on_submit(self):
        self.create_case_timeline_entry()
        self.schedule_deadline_notifications()

    def create_case_timeline_entry(self):
        frappe.get_doc({
            "doctype": "Comment",
            "comment_type": "Info",
            "reference_doctype": "Legal Case Registration",
            "reference_name": self.case_id,
            "content": self.get_timeline_text()
        }).insert(ignore_permissions=True)

    def get_timeline_text(self):
        text = f"""
        <b>Hearing Outcome Recorded</b><br>
        <b>Hearing Date:</b> {self.hearing_date}<br>
        <b>Outcome:</b> {self.hearing_outcome}
        """

        if self.next_hearing_date:
            text += f"<br><b>Next Hearing:</b> {self.next_hearing_date}"

        if self.filing_deadline:
            text += f"<br><b>Filing Deadline:</b> {self.filing_deadline}"

        if self.compliance_deadline:
            text += f"<br><b>Compliance Deadline:</b> {self.compliance_deadline}"

        return text

    def schedule_deadline_notifications(self):
        from nafed_erp.legal_and_vigilance.notifications import notify_case_event

        if self.filing_deadline:
            notify_case_event(
                case_id=self.case_id,
                event_type="Filing Deadline",
                message=f"Filing deadline on {self.filing_deadline}"
            )

        if self.compliance_deadline:
            notify_case_event(
                case_id=self.case_id,
                event_type="Compliance Deadline",
                message=f"Compliance deadline on {self.compliance_deadline}"
            )
