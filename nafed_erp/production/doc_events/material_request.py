import frappe
from frappe.model.mapper import get_mapped_doc


@frappe.whitelist()
def make_subcontracting_po(source_name, target_doc=None):

    def set_missing_values(source, target):
        target.is_subcontracted = 1
        target.supplier_warehouse = source.custom_supplier_warehouse

    def update_item(source, target, source_parent):

        # find subcontracting BOM
        sc_bom = frappe.db.get_value(
            "Subcontracting BOM",
            {"finished_good": source.item_code},
            ["service_item", "service_item_qty"],
            as_dict=True
        )

        if not sc_bom:
            frappe.throw(f"No Subcontracting BOM found for {source.item_code}")

        target.item_code = sc_bom.service_item
        target.qty = source.qty
        target.fg_item = source.item_code
        target.fg_item_qty = source.qty
        target.schedule_date = source.schedule_date

    doc = get_mapped_doc(
        "Material Request",
        source_name,
        {
            "Material Request": {
                "doctype": "Purchase Order",
                "validation": {"docstatus": ["=", 1]}
            },
            "Material Request Item": {
                "doctype": "Purchase Order Item",
                "postprocess": update_item
            }
        },
        target_doc,
        set_missing_values
    )

    return doc