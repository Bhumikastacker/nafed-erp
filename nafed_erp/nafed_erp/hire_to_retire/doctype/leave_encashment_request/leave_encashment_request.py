# Copyright (c) 2025, CSM Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
import frappe
from frappe.utils import flt
import frappe
from frappe.utils import get_url

class LeaveEncashmentRequest(Document):

    def validate(self):
        self.validate_leave_encashment()
        self.validate_approvers()
        # --- NEW CHANGE: Duplicate check call ---
        self.check_duplicate_request()

    def check_duplicate_request(self):
        """Check if a request already exists for the same employee, leave type and date"""
        existing = frappe.db.exists("Leave Encashment Request", {
            "employee": self.employee,
            "leave_type": self.leave_type,
            "request_date": self.request_date,
            "name": ("!=", self.name),
            "docstatus": ("<", 2) # To ignore canceled documents
        })

        if existing:
            frappe.throw(
                f"A Leave Encashment Request for <b>{self.leave_type}</b> has already been submitted for the date <b>{self.request_date}</b>. "
                f"Duplicate requests are not allowed."
            )

    def validate_approvers(self):
        if not self.leave_encashment_request_approvers:
            frappe.throw(
                "At least one Leave Encashment Approver is required before saving."
            )

    def validate_leave_encashment(self):
        available = self.available_balance or 0
        minimum = self.minimum_balance_for_encashment or 0

        # 🔹 1. Basic check: available must be >= minimum
        if available < minimum:
            frappe.throw(
                f"Available Balance ({available}) must be greater than or equal to "
                f"Minimum Balance for Encashment ({minimum}) to encash leave."
            )

        # 🔹 2. Calculate allowed encashable days (+1 as per your formula)
        encashable_days = available - minimum + 1
        if encashable_days < 0:
            encashable_days = 0

        # 🔹 3. Cannot encash more than allowed based on minimum balance rule
        if self.leave_days_to_encash and self.leave_days_to_encash > encashable_days:
            frappe.throw(
                f"You can encash a maximum of {encashable_days} days based on your balance for leave type '{self.leave_type}'. "
                f"You entered {self.leave_days_to_encash}."
            )
    
    def before_submit(self):
        self.status="Pending for Approval"


@frappe.whitelist()
def get_leave_encashment_approvers(employee):
    # Fetch employee doc ignoring permissions
    employee_doc = frappe.get_doc("Employee", employee)

    approvers = []

    for row in employee_doc.get("custom_leave_encashment_request_approvers", []):
        approvers.append({
            "request_approver_user_id": row.request_approver_user_id,
            "request_approver_name": row.request_approver_name
        })

    return approvers



@frappe.whitelist()
def create_encashment(source_name, target_doc=None):

    def update(doc, target):
        """
        Add custom logic AFTER mapping:
        - Fetch latest Salary Structure Assignment
        - Fetch base salary
        """

        # 1️⃣ Latest Salary Structure Assignment
        ssa = frappe.db.get_value(
            "Salary Structure Assignment",
            {
                "employee": doc.employee,
                "docstatus": 1
            },
            ["name", "salary_structure", "base"],
            order_by="from_date desc",
            as_dict=True
        )

        if ssa:
            target.salary_structure = ssa.salary_structure
            target.custom_salary_structure_assignment = ssa.name

    return get_mapped_doc(
        "Leave Encashment Request",
        source_name,
        {
            "Leave Encashment Request": {
                "doctype": "Leave Encashment",
                "field_map": {
                    "employee": "employee",
                    "leave_type": "leave_type",
                    "leave_days_to_encash": "encashment_days",
                    "request_date":"custom_encashment_request_date"
                }
            }
        },
        target_doc,
        update           # ⬅ post-process callback where we fill salary data
    )

@frappe.whitelist()
def update_status_and_notify(name, status):
    doc = frappe.get_doc("Leave Encashment Request", name)

    if doc.docstatus != 1:
        frappe.throw("Document must be submitted")
        
    if status not in ["Approved", "Rejected"]:
        frappe.throw("Invalid status")

    # Update status safely
    doc.db_set("status", status, update_modified=False)

    # Send email explicitly
    send_leave_encashment_email(doc)

    frappe.db.commit()
    return True

def send_leave_encashment_email(doc):
    employee = frappe.db.get_value(
        "Employee",
        doc.employee,
        ["employee_name", "user_id"],
        as_dict=True
    )

    if not employee or not employee.user_id:
        return

    email = frappe.db.get_value("User", employee.user_id, "email")
    if not email:
        return

    link = f"{get_url()}/app/leave-encashment-request/{doc.name}"

    frappe.sendmail(
        recipients=[email],
        subject=f"Leave Encashment Request {doc.name} {doc.status}",
        message=f"""
        Dear {employee.employee_name},<br><br>

        Your <b>Leave Encashment Request</b> has been
        <b>{doc.status}</b>.<br><br>

        <a href="{link}">View Request</a><br><br>

        Regards,<br>
        HR Team
        """,
        reference_doctype=doc.doctype,
        reference_name=doc.name,
        delayed=False
    )