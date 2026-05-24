# Copyright (c) 2026, CSM Technologies Pvt Ltd
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now
from frappe.utils import getdate, today


class LegalCaseHearing(Document):
    def before_save(self):
        self.set_document_metadata()

    def validate(self):
        self.validate_other_hearing_type()
        self.validate_hearing_dates()

    def set_document_metadata(self):
        """
        Auto-fill uploaded_by and uploaded_on
        for hearing document child table
        """
        for row in self.hearing_documents:
            if row.file and not row.uploaded_by:
                row.uploaded_by = frappe.session.user
                row.uploaded_on = now()

    def validate_hearing_dates(self):

        today_date = getdate(today())

        # Previous Hearing Date validations
        if self.previous_hearing_date:

            if getdate(self.previous_hearing_date) == getdate(self.hearing_date):
                frappe.throw("Previous Hearing Date cannot be equal to Hearing Date.")

            if getdate(self.previous_hearing_date) > today_date:
                frappe.throw("Previous Hearing Date cannot be a future date.")

        # Next Hearing Date validations
        if self.next_hearing_date:

            if getdate(self.next_hearing_date) <= getdate(self.hearing_date):
                frappe.throw("Next Hearing Date must be a future date.")

    def validate_other_hearing_type(self):
        if self.hearing_type == "Other":
            self.other_hearing_type = (
                self.other_hearing_type.strip()
                if self.other_hearing_type
                else None
            )
        else:
            self.other_hearing_type = None


def get_last_other_hearing_type(case_id):
    return frappe.db.get_value(
        "Legal Case Hearing",
        {
            "case_id": case_id,
            "hearing_type": "Other",
            "other_hearing_type": ["is", "set"]
        },
        "other_hearing_type",
        order_by="hearing_date desc"
    )

@frappe.whitelist()
def schedule_hearing(
    case_id,
    hearing_date,
    hearing_type,
    venue=None,
    advocate=None,
    remarks=None,
    next_hearing_date=None, 
    other_hearing_type=None, 
    has_next_hearing=None     
):
# --------------------------------
    # OTHER HEARING TYPE HANDLING
    # --------------------------------
    if hearing_type == "Other":
        if other_hearing_type:
            other_hearing_type = other_hearing_type.strip()
            if not other_hearing_type:
                other_hearing_type = None

        if not other_hearing_type:
            other_hearing_type = get_last_other_hearing_type(case_id)
    else:
        other_hearing_type = None

    # --------------------------------
    # CREATE HEARING
    # --------------------------------
    hearing = frappe.get_doc({
        "doctype": "Legal Case Hearing",
        "case_id": case_id,
        "hearing_date": hearing_date,
        "next_hearing_date": next_hearing_date if has_next_hearing else None,
        "hearing_type": hearing_type,
        "other_hearing_type": other_hearing_type,
        "venue": venue,
        "advocate": advocate,
        "remarks": remarks
    }).insert(ignore_permissions=True)

    # --------------------------------
    # NOTIFICATION
    # --------------------------------
    from nafed_erp.legal_and_vigilance.notifications import notify_case_event

    notify_case_event(
        case_id=case_id,
        event_type="Hearing Scheduled",
        message=f"Hearing scheduled on {hearing_date} ({hearing_type})"
    )

    return hearing.name
