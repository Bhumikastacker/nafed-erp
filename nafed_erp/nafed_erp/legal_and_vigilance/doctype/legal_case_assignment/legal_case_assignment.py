# # # Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
# # # For license information, please see license.txt

import frappe
from frappe.utils import now
from frappe.model.document import Document


# ---------------------------------------------------------
# Helper: Update Current Active Cases for Advocate
# ---------------------------------------------------------
def update_current_active_cases(lawyer):
    """
    Recalculate and update current_active_cases
    in Legal Advocates doctype
    """
    active_cases = frappe.db.count(
        "Legal Case Assignment",
        {
            "lawyer": lawyer,
            "status": "Active"
        }
    )

    frappe.db.set_value(
        "Legal Advocates",
        lawyer,
        "current_active_cases",
        active_cases
    )


# ---------------------------------------------------------
# Assignment History Logger
# ---------------------------------------------------------
def log_assignment_history(
    case_id,
    old_advocate,
    new_advocate,
    # lawyer_type,
    remarks=None
):
    frappe.get_doc({
        "doctype": "Legal Case Assignment History",
        "case_id": case_id,
        "lawyer": new_advocate,
        # "lawyer_type": lawyer_type,
        "action": "Reassigned" if old_advocate else "Assigned",
        "action_by": frappe.session.user,
        "action_date": now(),
        "remarks": (
            f"Old Advocate: {old_advocate or 'None'} → New Advocate: {new_advocate}"
            + (f"\n{remarks}" if remarks else "")
        )
    }).insert(ignore_permissions=True)


# ---------------------------------------------------------
# Legal Case Assignment Doctype
# ---------------------------------------------------------
class LegalCaseAssignment(Document):
    pass


# ---------------------------------------------------------
# Assign / Reassign Case API
# ---------------------------------------------------------
@frappe.whitelist()
def assign_case(
    case_id,
    lawyer,
    permission_start_date,
    # lawyer_type=None,
    expiry_date=None,
    delegation_status="Primary",
    remarks=None
):
    """
    Assign / Reassign a legal case to an advocate
    """

    # ---------------------------
    # Fetch Case & Advocate
    # ---------------------------
    case = frappe.get_doc("Legal Case Registration", case_id)
    old_advocate = case.assigned_advocate

    advocate = frappe.get_doc("Legal Advocates", lawyer)

    # ---------------------------
    # Lawyer Type
    # ---------------------------
    # if not lawyer_type:
    # lawyer_type = advocate.advocate_type

    # if not lawyer_type:
    #     frappe.throw("Advocate Type is mandatory")

    # ---------------------------
    # Empanelment Check
    # ---------------------------
    # if lawyer_type == "Empanelment External Advocate":
    #     if not advocate.empanelled or advocate.empanelment_status != "Active":
    #         frappe.throw("Selected advocate is not empanelled or inactive")
    if not advocate.empanelled or advocate.empanelment_status != "Active":
        frappe.throw("Selected advocate is not empanelled or inactive")

    # ---------------------------
    # Conflict Check
    # ---------------------------
    if frappe.db.exists(
        "Legal Case Assignment",
        {
            "case_id": case_id,
            "lawyer": lawyer,
            "status": "Active"
        }
    ):
        frappe.throw("Conflict detected: advocate already assigned to this case")

    # ---------------------------
    # Workload Check
    # ---------------------------
    active_cases = frappe.db.count(
        "Legal Case Assignment",
        {
            "lawyer": lawyer,
            "status": "Active"
        }
    )

    if advocate.max_active_cases and active_cases >= advocate.max_active_cases:
        frappe.throw("Advocate workload exceeded")

    # ---------------------------
    # Close Old Assignments
    # ---------------------------
    frappe.db.sql(
        """
        UPDATE `tabLegal Case Assignment`
        SET status = 'Closed',
            closed_on = %s,
            closed_by = %s
        WHERE case_id = %s
          AND status = 'Active'
        """,
        (now(), frappe.session.user, case_id)
    )

    # ---------------------------
    # Update Old Advocate Count
    # ---------------------------
    if old_advocate:
        update_current_active_cases(old_advocate)

    # ---------------------------
    # Create New Assignment
    # ---------------------------
    assignment = frappe.get_doc({
        "doctype": "Legal Case Assignment",
        "case_id": case_id,
        "lawyer": lawyer,
        # "lawyer_type": lawyer_type,
        "permission_start_date": permission_start_date,
        "expiry_date": expiry_date,
        "delegation_status": delegation_status,
        "assigned_by": frappe.session.user,
        "assigned_on": now(),
        "status": "Active"
    }).insert(ignore_permissions=True)

    # ---------------------------
    # Update New Advocate Count
    # ---------------------------
    update_current_active_cases(lawyer)

    # ---------------------------
    # Update Case Master
    # ---------------------------
    case.assigned_advocate = lawyer
    case.save(ignore_permissions=True)

    # ---------------------------
    # Assignment History
    # ---------------------------
    log_assignment_history(
        case_id=case_id,
        old_advocate=old_advocate,
        new_advocate=lawyer,
        # lawyer_type=lawyer_type,
        remarks=remarks
    )

    return assignment.name

