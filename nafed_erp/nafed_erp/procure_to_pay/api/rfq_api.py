import frappe
import json

@frappe.whitelist()
def get_item_suppliers(item_codes):

    items = json.loads(item_codes)

    # Get supplier list from Item Supplier
    item_suppliers = frappe.get_all(
        "Item Supplier",
        filters={"parent": ["in", items]},
        fields=["supplier"]
    )

    # Get unique supplier names
    supplier_names = list(set([d.supplier for d in item_suppliers if d.supplier]))

    if not supplier_names:
        return []

    # Fetch email_id from Supplier doctype
    suppliers = frappe.get_all(
        "Supplier",
        filters={"name": ["in", supplier_names]},
        fields=["name", "email_id"]
    )
    return suppliers
    
    # Remove duplicate suppliers and return a unique list
    return list(set([d.supplier for d in suppliers]))

# @frappe.whitelist()
# def get_item_by_barcode(barcode):

#     result = frappe.get_all(
#         "Item Barcode",
#         filters={
#             "barcode": barcode
#         },
#         fields=[
#             "parent",
#             "custom_mrp"
#         ],
#         limit=1
#     )

#     if result:
#         return {
#             "item_code": result[0].parent,
#             "rate": result[0].custom_mrp
#         }

#     return {}

# @frappe.whitelist()
# def get_item_by_barcode(barcode):

#     result = frappe.get_all(
#         "Item Barcode",
#         filters={"barcode": barcode},
#         fields=["parent", "custom_mrp"],
#         limit=1
#     )

#     if result:
#         return {
#             "item_code": result[0].parent,
#             "price_list_rate": result[0].custom_mrp   # ✅ IMPORTANT CHANGE
#         }

#     return {}

# import frappe

# @frappe.whitelist()
# def get_item_by_barcode(barcode):
#     # Fetch the Item Barcode child table row
#     barcode_row = frappe.db.get_value(
#         "Item Barcode",
#         {"barcode": barcode},
#         ["parent", "custom_mrp", "uom"],
#         as_dict=True
#     )
#     if not barcode_row:
#         return None

#     item_code = barcode_row.parent
#     mrp = barcode_row.custom_mrp

#     if not mrp:
#         # Fallback to item's standard selling price if MRP not set
#         mrp = frappe.db.get_value("Item", item_code, "standard_selling_rate")

#     return {
#         "item_code": item_code,
#         "rate": mrp,
#         "price_list_rate": mrp,
#         "uom": barcode_row.uom,
#         "barcode": barcode
#     }
import frappe

@frappe.whitelist(allow_guest=False)
def get_item_by_barcode(barcode):
    result = frappe.db.sql("""
        SELECT
            ib.parent AS item_code,
            i.item_name,
            i.stock_uom,
            ib.uom,
            ib.custom_mrp AS rate
        FROM `tabItem Barcode` ib
        INNER JOIN `tabItem` i ON i.name = ib.parent
        WHERE ib.barcode = %s
        LIMIT 1
    """, barcode, as_dict=True)

    if not result:
        return None

    row = result[0]

    return {
        "item_code": row.item_code,   # "OS"
        "item_name": row.item_name,   # "Oil Seed"
        "rate": row.rate,             # from custom_mrp per barcode row
        "uom": row.uom or row.stock_uom,
    }
