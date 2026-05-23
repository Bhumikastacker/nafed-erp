import frappe
from frappe.model.document import Document
from frappe.utils import nowdate
import json


class TrainingRequisition(Document):

    def validate(self):
        # 1. Check empty employee table
        if self.external_type == "Study Tours":
            return
            
        if not self.employee_details:
            frappe.throw(
                msg="Please add at least one employee to the Employee Details table",
                title="Missing Employees"
            )

        # 2. Check missing employee in rows
        invalid_rows = []
        for row in self.employee_details:
            if not row.employee:
                invalid_rows.append(str(row.idx))

        if invalid_rows:
            frappe.throw(
                msg=f"Employee is required in row(s): {', '.join(invalid_rows)}",
                title="Incomplete Data"
            )

        # 3. Check duplicate employees
        seen = set()
        duplicate_rows = []

        for row in self.employee_details:
            emp = row.employee
            if emp in seen:
                duplicate_rows.append(str(row.idx))
            else:
                seen.add(emp)

        if duplicate_rows:
            frappe.throw(
                msg=f"Duplicate employee found in row(s): {', '.join(duplicate_rows)}",
                title="Duplicate Employees"
            )

    def on_submit(self):
        self.status = "Submitted"

    # ----------------------------
    # UC-TR-02: APPROVAL PROCESS
    # ----------------------------
    def on_update(self):
        # APPROVED
        if self.status == "Approved":
            self.approved_by = frappe.session.user
            self.approval_date = frappe.utils.today()
            self.flags.ignore_validate_update_after_submit = True
            frappe.msgprint("Training Requisition Approved & Locked")

        # REJECTED
        if self.status == "Rejected":
            frappe.msgprint("Training Requisition has been Rejected.")

    def before_submit(self):
        if self.external_type == "Training" or self.internal_type == "Training":
            je = frappe.new_doc("Journal Entry")
            je.posting_date = nowdate()
            je.company = self.branch
            je.voucher_type = "Journal Entry"
            je.custom_training_requisition = self.name

            amount = self.budget_amount

            # -------- Row 1: DEBIT --------
            je.append("accounts", {
                "account": self.debit_account,
                "debit_in_account_currency": amount,
                "cost_center": self.cost_center
            })

            # -------- Row 2: CREDIT --------
            je.append("accounts", {
                "account": self.credit_account,
                "credit_in_account_currency": amount,
                "cost_center": self.cost_center
            })

            je.insert(ignore_permissions=True)
            je.submit()


@frappe.whitelist()
def get_employees(doc):
    # doc comes as JSON string → convert to dict
    if isinstance(doc, str):
        doc = json.loads(doc)
    doc = frappe._dict(doc)

    filters = {}

    # Build filters
    if doc.get("custom_division"):
        filters["custom_division"] = doc.get("custom_division")
    if doc.get("designation"):
        filters["designation"] = doc.get("designation")
    if doc.get("employment_type"):
        filters["employment_type"] = doc.get("employment_type")
    if doc.get("company"):
        filters["company"] = doc.get("company")
    if doc.get("branch"):
        # NOTE: tumne yaha branch ka key mismatch kiya tha
        filters["branch"] = doc.get("employee_branch")
    if doc.get("department"):
        filters["department"] = doc.get("department")
    if doc.get("grade"):
        filters["grade"] = doc.get("grade")

    # CONDITION 1: No filters selected
    if not filters:
        frappe.throw("Please add at least one filter before fetching employees.")

    # Fetch employees
    employees = frappe.get_all("Employee", filters=filters, fields=["name"])

    # CONDITION 2: Filters added but no employee found
    if not employees:
        frappe.throw("No employee found for the selected filters.")

    return employees
