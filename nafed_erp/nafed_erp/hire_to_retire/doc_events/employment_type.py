import frappe

def validate_date(doc, method=None):
    if doc.custom_payroll_entry_date <= 0 or doc.custom_payroll_entry_date >31:
        frappe.throw("Payroll Entry date can not be less then 1 and greater than 31")
