import frappe
import json
from frappe.model.document import Document


class BranchPaymentRequest(Document):
    def before_insert(self):
        # default status can be handled on submit
        if self.head_office == self.branch:
            frappe.throw("HeadOffice and Branch Cannot be same")
        calculate_grand_total(self)

    def on_submit(self):
        # set status automatically when submitted
        self.send_email_notification()

    def on_cancel(self):
        # set status automatically when submitted
        self.db_set("status", "Cancelled")

    def send_email_notification(self):
        recipients = []
        # use existing field if present
        if getattr(self, "email_to", None):
            recipients.append(self.email_to)
        # or hard-code a default
        else:
            recipients.append("Administrator")

        if not recipients:
            return

        frappe.sendmail(
            recipients=recipients,
            subject=f"Payment Request Created - {self.name}",
            message=f"""
                Dear Team,<br><br>
                A new payment request <b>{self.name}</b> has been created.<br>
                Reference: {self.reference_doctype} - {self.reference_name}<br>
                Amount: {getattr(self, 'grand_total', getattr(self, 'amount', 0))}<br><br>
                Regards,<br>
                ERP System
            """
        )


@frappe.whitelist()
def resend_alert_email(docname):
    """Manual resend email button function"""
    doc = frappe.get_doc("Branch Payment Request", docname)
    doc.send_email_notification()
    return "Email Sent"


def update_payment_request_status(doc, method):
    if not doc.custom_payment_request_branch:
        return

    try:
        payment_req = frappe.get_doc(
            "Branch Payment Request",
            doc.custom_payment_request_branch
        )
    except frappe.DoesNotExistError:
        return

    payment_req.db_set("status", "Fund Released")
    payment_req.db_set("workflow_state", "Fund Released")


from frappe.utils import nowdate

@frappe.whitelist()
def create_payment_entry(docname):
    """
    Create a Payment Entry (in draft mode) from a Branch Payment Request.
    Returns prefilled document data, not submitted.
    """
    source_doc = frappe.get_doc("Branch Payment Request", docname)

    # Build Payment Entry data
    payment_entry_data = {
        "doctype": "Payment Entry",
        "posting_date": nowdate(),
        "party_type": source_doc.party_type,
        "party": source_doc.party,
        "party_name": source_doc.party_name,
        "mode_of_payment": source_doc.mode_of_payment,
        "company": source_doc.head_office,
        "payment_type": "Pay",
        "paid_to": source_doc.get("paid_to") or "",
        "paid_to_account_currency": "INR",
        "paid_amount": source_doc.grand_total,
        "base_paid_amount": source_doc.grand_total,
        "received_amount": source_doc.grand_total,
        "target_exchange_rate": 1,
        "custom_payment_request_branch": source_doc.name,
        "references": [
            {
                "doctype": "Payment Entry Reference",
                "parentfield": "references",
                "reference_doctype": source_doc.reference_doctype,
                "reference_name": source_doc.reference_name,
                "total_amount": source_doc.grand_total,
                "allocated_amount": source_doc.grand_total,
                "outstanding_amount": source_doc.outstanding_amount or source_doc.grand_total,
                "due_date": nowdate(),
            }
        ],
        "reference_no": source_doc.get("reference_no"),
        "reference_date": source_doc.get("reference_date"),
    }

    # Create but don’t submit or save yet
    payment_entry = frappe.new_doc("Payment Entry")
    payment_entry.update(payment_entry_data)

    # Return as JSON so it opens as draft form
    return payment_entry.as_dict()

@frappe.whitelist()
def branch_payment_entry(docname):
    """
    Create a Payment Entry (in draft mode) from a Branch Payment Request.
    Returns prefilled document data, not submitted.
    """
    source_doc = frappe.get_doc("Branch Payment Request", docname)

    # Build Payment Entry data
    payment_entry_data = {
        "doctype": "Payment Entry",
        "posting_date": nowdate(),
        "party_type": source_doc.party_type,
        "party": source_doc.party,
        "party_name": source_doc.party_name,
        "mode_of_payment": source_doc.mode_of_payment,
        "company": source_doc.branch,
        "payment_type": "Receive",
        "paid_to": source_doc.get("paid_to") or "",
        "paid_to_account_currency": "INR",
        "paid_amount": source_doc.grand_total,
        "base_paid_amount": source_doc.grand_total,
        "received_amount": source_doc.grand_total,
        "target_exchange_rate": 1,
        "custom_payment_request_branch": source_doc.name,
        "references": [
            {
                "doctype": "Payment Entry Reference",
                "parentfield": "references",
                "reference_doctype": source_doc.reference_doctype,
                "reference_name": source_doc.reference_name,
                "total_amount": source_doc.grand_total,
                "allocated_amount": source_doc.grand_total,
                "outstanding_amount": source_doc.outstanding_amount or source_doc.grand_total,
                "due_date": nowdate(),
            }
        ],
        "reference_no": source_doc.get("reference_no"),
        "reference_date": source_doc.get("reference_date"),
    }

    # Create but don’t submit or save yet
    payment_entry = frappe.new_doc("Payment Entry")
    payment_entry.update(payment_entry_data)

    # Return as JSON so it opens as draft form
    return payment_entry.as_dict()

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
        filters["branch"] = doc.get("employee_branch")
    if doc.get("department"):
        filters["department"] = doc.get("department")
    if doc.get("grade"):
        filters["grade"] = doc.get("grade")

    # ---------------------------------------------
    # CONDITION 1: No filters selected
    # ---------------------------------------------
    if not filters:
        frappe.throw("Please add at least one filter before fetching employees.")

    # Fetch employees
    employees = frappe.get_all("Employee", filters=filters, fields=["name"])

    # ---------------------------------------------
    # CONDITION 2: Filters added but no employee found
    # ---------------------------------------------
    if not employees:
        frappe.throw("No employee found for the selected filters.")

    return employees

def calculate_grand_total(doc, method=None):
    total = 0

    if doc.employee_salary_details:
        for row in doc.employee_salary_details:
            total += float(row.amount or 0)

    doc.grand_total = total
