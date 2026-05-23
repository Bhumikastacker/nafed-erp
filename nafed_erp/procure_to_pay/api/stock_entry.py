import frappe

@frappe.whitelist()
def create_po_from_indent(stock_entry):

    ste = frappe.get_doc("Stock Entry", stock_entry)

    supplier = frappe.db.get_value("Supplier", {}, "name")

    if not supplier:
        frappe.throw("No Supplier found")

    po = frappe.new_doc("Purchase Order")
    po.supplier = supplier

    has_shortage = False

    for item in ste.items:

        requested_qty = getattr(item, "custom_requested_qty", None) or item.qty

        available_qty = frappe.db.get_value(
            "Bin",
            {
                "item_code": item.item_code,
                "warehouse": item.s_warehouse
            },
            "actual_qty"
        ) or 0

        # ✅ SAFE SHORTAGE
        shortage = max(0, requested_qty - available_qty)

        if shortage <= 0:
            continue

        has_shortage = True

        po.append("items", {
            "item_code": item.item_code,
            "qty": shortage,
            "schedule_date": frappe.utils.nowdate(),
            "warehouse": item.t_warehouse
        })

    if not has_shortage:
        frappe.throw("No shortage items to create PO")

    po.insert()
    po.submit()

    return po.name


def calculate_indent_data(doc, method=None):

    requested_qty = 0
    available_qty_total = 0

    fully_available = 0
    partially_available = 0
    not_available = 0

    requested_sku = len(doc.items)

    for item in doc.items:

        available_qty = frappe.db.get_value(
            "Bin",
            {
                "item_code": item.item_code,
                "warehouse": item.s_warehouse
            },
            "actual_qty"
        ) or 0

        req_qty = item.qty

        used_qty = min(available_qty, req_qty)

        difference = req_qty - used_qty

        # CHILD VALUES
        item.custom_requested_qty = req_qty


        item.custom_difference_qty = difference

        item.custom_fully_available = (
            req_qty if available_qty >= req_qty else 0
        )

        item.custom_partially_available = (
            used_qty if 0 < available_qty < req_qty else 0
        )

        # TOTALS
        requested_qty += req_qty

        available_qty_total += used_qty

        if available_qty >= req_qty:

            fully_available += req_qty

        elif available_qty > 0:

            partially_available += used_qty

        else:

            not_available += req_qty

    # PARENT TOTALS
    doc.custom_requested_sku = requested_sku

    doc.custom_requested_qty = requested_qty

    doc.custom_available_qty = available_qty_total

    doc.custom_difference_qty = (
        requested_qty - available_qty_total
    )

    doc.custom_fully_available = fully_available

    doc.custom_partially_available = partially_available
