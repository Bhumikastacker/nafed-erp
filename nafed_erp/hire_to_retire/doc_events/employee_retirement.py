import frappe
from frappe.utils import today

def create_employee_separation_on_retirement(doc, method):

    # ✅ Run only if date_of_retirement is filled
    if not doc.date_of_retirement:
        return

    # ✅ Check if Employee Separation already exists
    existing = frappe.db.exists("Employee Separation", {
        "employee": doc.name,
        "custom_employee_sepstation_type": "Superannuation"
    })

    # ✅ CASE 1: Agar pehle se bana hua hai → UPDATE karo
    if existing:
        sep = frappe.get_doc("Employee Separation", existing)

        # ✅ Sirf DRAFT me hi update ho
        if sep.docstatus == 0:
            sep.boarding_begins_on = doc.date_of_retirement
            sep.department = doc.department
            sep.designation = doc.designation
            sep.company = doc.company
            sep.save(ignore_permissions=True)
            frappe.db.commit()

        return

    # ✅ CASE 2: Agar pehle se nahi hai → CREATE karo
    sep = frappe.new_doc("Employee Separation")
    sep.employee = doc.name
    sep.employee_name = doc.employee_name
    sep.department = doc.department
    sep.designation = doc.designation
    sep.company = doc.company

    sep.custom_employee_sepstation_type = "Superannuation"
    sep.boarding_status = "Pending"
    sep.boarding_begins_on = doc.date_of_retirement

    # ✅ Keep it in DRAFT
    sep.docstatus = 0

    sep.insert(ignore_permissions=True)
    frappe.db.commit()
    
