# Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now
from nafed_erp.legal_and_vigilance.notifications import notify_case_event

@frappe.whitelist()
def update_case_status(
    case_id,
    # case_classification,
    case_status,
    description=None,
    other_case_status=None
    ):
    case = frappe.get_doc("Legal Case Registration", case_id)

    # ---------------------------------
    # Update main case status
    # ---------------------------------
    case.db_set("case_status", case_status)

    # ---------------------------------
    # Clean "Other" value properly
    # ---------------------------------
    if case_status == "Other":
        other_case_status = (
            other_case_status.strip()
            if other_case_status
            else None
        )
    else:
        other_case_status = None

    case = frappe.get_doc("Legal Case Registration", case_id)
    case.db_set("case_status", case_status)
    frappe.get_doc({
        "doctype": "Legal Case Status Log",
        "case_id": case_id,
        # "case_classification": case_classification,
        "case_status": case_status,
        "other_case_status": other_case_status,
        "updated_by": frappe.session.user,
        "updated_on": now(),
        "description": description
    }).insert(ignore_permissions=True)
    # ---------------------------------
    # Trigger notification (UC_LEG_008)
    # ---------------------------------
    notify_case_event(
        case_id=case_id,
        event_type="Status Change",
        message=f"Case status updated to <b>{case_status}</b>"
    )

    return {
        "status": "success",
        "case_status": case_status
    }

class LegalCaseRegistration(Document):
    # def validate(self):
    #     self.check_duplicate_case()
    #     if self.is_new():
    #         return
    #     from nafed_erp.legal_and_vigilance.permissions import has_case_access

    #     if not has_case_access(self.name, "Write"):
    #         frappe.throw("You are not authorized to edit this case")
            
    # def on_trash(self):
    #     from nafed_erp.legal_and_vigilance.permissions import has_case_access
    #     if not has_case_access(self.name, "Write"):
    #         frappe.throw("You are not authorized to delete this case")
    
    # def on_update(self):
    #     if self.status == "Registered":
    #         frappe.msgprint("Legal Case Registered Successfully.")
    #         # frappe.sendmail(
    #         #     recipients=[self.assigned_advocate],
    #         #     subject=f"New Legal Case Assigned: {self.name}",
    #         #     message=f"You have been assigned to Legal Case {self.name}"
    #         # )

    def check_duplicate_case(self):
        existing = frappe.db.exists(
            "Legal Case Registration",
            {
                "party_name": self.party_name,
                "jurisdiction": self.jurisdiction,
                "docstatus": ["!=", 2]
            }
        )
        if existing and existing != self.name:
            frappe.throw(
                f"Duplicate case detected. Existing Case: {existing}. Please link instead."
            )
    

    def validate(self):
        self.validate_assigned_advocate()
        self.validate_other_case_category()


    def validate_other_case_category(self):
        if self.case_category == "Other":
        # allow empty, but clean garbage
            self.other_case_category = (
            self.other_case_category.strip()
            if self.other_case_category
            else None
        )
        else:
            self.other_case_category = None

    def validate_assigned_advocate(self):
        if not self.assigned_advocate:
            return

        empanelment_status = frappe.db.get_value(
            "Legal Advocates",
            self.assigned_advocate,
            "empanelment_status"
        )

        if empanelment_status in ["Suspended", "Expired"]:
            frappe.throw(
                f"Advocate '{self.assigned_advocate}' cannot be assigned because "
                f"their empanelment status is '{empanelment_status}'."
            )
        
