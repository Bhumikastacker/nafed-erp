import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_field

def create_custom_fields():
    """Create custom fields in HR Settings after migration"""

    custom_fields = {
        "HR Settings": [
            {
                "fieldname": "children_allowance_min_age_limit",
                "label": "Children Allowance Declaration Min Age Limit",
                "fieldtype": "Int",
                "insert_after": "employee_records_to_be_filled_by"
            },
            {
                "fieldname": "children_allowance_max_age_limit",
                "label": "Children Allowance Declaration Max Age Limit",
                "fieldtype": "Int",
                "insert_after": "children_allowance_min_age_limit"
            },
            {
                "fieldname": "children_allowance_amount",
                "label": "Children Allowance Amount",
                "fieldtype": "Currency",
                "insert_after": "children_allowance_max_age_limit"
            }
        ]
    }

    for doctype, fields in custom_fields.items():
        for field in fields:
            try:
                create_custom_field(doctype, field)
                frappe.db.commit()
            except Exception as e:
                frappe.log_error(frappe.get_traceback(), "Custom Field Creation Failed")
