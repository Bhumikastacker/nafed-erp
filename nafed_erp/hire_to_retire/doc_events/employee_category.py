import frappe
from frappe import _

# ==========================================================
# Employee Category name should not be purely numeric
# ==========================================================
def validate_category_name(doc, method):
    if doc.employee_category_name and doc.employee_category_name.isdigit():

        frappe.throw(
            _("Employee Category name '{0}' is invalid. Purely numeric names are not allowed.")
            .format(doc.employee_category_name)
        )