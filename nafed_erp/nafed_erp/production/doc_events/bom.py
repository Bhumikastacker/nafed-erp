import frappe

def create_subcontracting_bom(doc, method):

    # get finished item
    item = frappe.get_doc("Item", doc.item)

    # run only if item is marked subcontracted
    if not item.is_sub_contracted_item or not item.custom_create_service_item:
        return

    # assume service item follows your naming rule
    service_item = f"{doc.item}-SERVICE"

    if not frappe.db.exists("Item", service_item):
        frappe.throw(f"Service Item {service_item} not found")

    # prevent duplicate subcontracting BOM and set is_active as 0 for old BOM if exists and then create new one with is_active 1
    if frappe.db.exists("Subcontracting BOM", {
        "finished_good": doc.item,
        "is_active": 1
    }):
        # Set is_active as 0 for existing subcontracting BOM
        frappe.db.set_value("Subcontracting BOM", {
            "finished_good": doc.item,
            "is_active": 1
        }, "is_active", 0)

    sc_bom = frappe.new_doc("Subcontracting BOM")

    sc_bom.finished_good = doc.item
    sc_bom.finished_good_qty = doc.quantity
    sc_bom.finished_good_uom = doc.uom
    sc_bom.finished_good_bom = doc.name

    sc_bom.service_item = service_item
    sc_bom.service_item_qty = 1
    sc_bom.service_item_uom = doc.uom

    sc_bom.conversion_factor = 1
    sc_bom.company = doc.company

    sc_bom.insert(ignore_permissions=True)

    frappe.msgprint(f"Subcontracting BOM {sc_bom.name} created.")