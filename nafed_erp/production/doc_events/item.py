import frappe

def create_service_item_for_subcontracting(doc, method):
    
    # run only if checkbox enabled
    if not doc.custom_create_service_item:
        return

    service_item_code = f"{doc.item_code}-SERVICE"

    # prevent duplicate creation
    if frappe.db.exists("Item", service_item_code):
        return

    service_item = frappe.new_doc("Item")
    service_item.item_code = service_item_code
    service_item.item_name = f"{doc.item_name} Service"
    service_item.item_group = "Services"
    service_item.stock_uom = doc.stock_uom
    service_item.is_stock_item = 0
    service_item.is_purchase_item = 1
    service_item.is_sales_item = 0
    service_item.custom_finished_good = doc.name  # optional custom link

    service_item.insert(ignore_permissions=True)
    doc.is_sub_contracted_item = 1
    doc.save(ignore_permissions=True)
    frappe.msgprint(f"Service Item {service_item.name} created.")