import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def add_noting_sheet_to_all_modules():
    excluded_modules = ["Legal and Vigilance", "Estates"]
    target_doctypes = frappe.get_all("DocType", filters={"module": ["not in", excluded_modules], "istable": 0, "issingle": 0}, pluck="name")

    for dt in target_doctypes:
        if frappe.db.exists("Custom Field", {"dt": dt, "fieldname": "logs"}):
            continue

        try:
            meta = frappe.get_meta(dt)
            fields = meta.fields
            
            # Logic to find the end of the first tab
            second_tab_index = -1
            tab_count = 0
            for i, f in enumerate(fields):
                if f.fieldtype == 'Tab Break':
                    tab_count += 1
                    if tab_count == 2:
                        second_tab_index = i
                        break
            
            target_field = fields[second_tab_index - 1].fieldname if second_tab_index > 0 else (fields[-1].fieldname if fields else "")

            custom_fields = [
                {"fieldname": "sb_noting_sheet", "label": "Noting Sheet", "fieldtype": "Section Break", "insert_after": target_field},
                {"fieldname": "logs", "label": "Noting Sheet", "fieldtype": "Table", "options": "Complaint Receipts Remarks", "insert_after": "sb_noting_sheet"}
            ]
            create_custom_fields({dt: custom_fields}, ignore_validate=True)
        except Exception:
            pass



def remove_noting_sheet_from_auction():
    try:
        # Remove child table field: logs
        if frappe.db.exists("Custom Field", {"dt": "Auction", "fieldname": "logs"}):
            custom_field_name = frappe.db.get_value(
                "Custom Field",
                {"dt": "Auction", "fieldname": "logs"},
                "name"
            )
            frappe.delete_doc("Custom Field", custom_field_name, force=1)

        # Remove section break: sb_noting_sheet
        if frappe.db.exists("Custom Field", {"dt": "Auction", "fieldname": "sb_noting_sheet"}):
            custom_field_name = frappe.db.get_value(
                "Custom Field",
                {"dt": "Auction", "fieldname": "sb_noting_sheet"},
                "name"
            )
            frappe.delete_doc("Custom Field", custom_field_name, force=1)

        frappe.db.commit()
        frappe.msgprint("Noting Sheet removed successfully from Auction Doctype")

    except Exception as e:
        frappe.log_error(
            title="Failed to remove Noting Sheet from Auction",
            message=str(e)
        )
        frappe.throw(str(e))