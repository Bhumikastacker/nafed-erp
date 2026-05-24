import frappe
from frappe.utils import flt

@frappe.whitelist()
def create_indent(mr_list):

    mr_list = frappe.parse_json(mr_list)

    stock_entry = frappe.new_doc("Stock Entry")
    stock_entry.stock_entry_type = "Material Transfer"

    # 🔥 STEP 1: GROUP ITEM WISE
    item_map = {}

    for mr in mr_list:

      mr_doc = frappe.get_doc("Material Request", mr)

    # 🔥 SET COMPANY
    if not stock_entry.company:

        stock_entry.company = mr_doc.company

    elif stock_entry.company != mr_doc.company:

        frappe.throw(
            "All Material Requests must belong to same Company"
        )

    # 🔥 ITEM LOOP
    for item in mr_doc.items:

            key = (
                item.item_code,
                item.warehouse,                 # TARGET WAREHOUSE
                mr_doc.set_from_warehouse      # SOURCE WAREHOUSE
            )

            if key not in item_map:

                item_map[key] = {
                    "qty": 0,
                    "target_wh": item.warehouse,
                    "source_wh": mr_doc.set_from_warehouse
                }

            item_map[key]["qty"] += flt(item.qty)

    # 🔥 STEP 2: INIT TOTALS
    requested_sku = len(item_map)

    requested_qty = 0
    available_qty_total = 0

    fully_available = 0
    partially_available = 0
    not_available = 0

    # 🔥 STEP 3: LOOP ITEMS
    for (item_code, target_wh, source_wh), data in item_map.items():

        req_qty = data["qty"]

        # 🔥 FETCH STOCK ONLY FROM SOURCE WAREHOUSE
        available_qty = frappe.db.get_value(
            "Bin",
            {
                "item_code": item_code,
                "warehouse": source_wh
            },
            "actual_qty"
        ) or 0

        # 🔥 CALCULATIONS
        used_qty = min(available_qty, req_qty)

        difference = req_qty - used_qty

        # 🔥 TOTALS
        requested_qty += req_qty

        available_qty_total += used_qty

        # 🔥 FULL / PARTIAL / NOT
        if available_qty >= req_qty:

            fully_available += req_qty

        elif available_qty > 0:

            partially_available += used_qty

        else:

            not_available += req_qty

        # 🔥 ADD STOCK ENTRY ROW
        stock_entry.append("items", {

            "item_code": item_code,

            # REQUESTED QTY
            "qty": req_qty,

            # WAREHOUSES
            "s_warehouse": source_wh,
            "t_warehouse": target_wh,

            # CUSTOM FIELDS
            "custom_requested_qty": req_qty,

            "custom_available_qty": available_qty,

            "custom_difference_qty": difference,

            "custom_fully_available":
                req_qty if available_qty >= req_qty else 0,

            "custom_partially_available":
                used_qty if 0 < available_qty < req_qty else 0
        })

    # 🔥 FINAL TOTALS
    difference_qty = requested_qty - available_qty_total

    stock_entry.custom_requested_sku = requested_sku

    stock_entry.custom_requested_qty = requested_qty

    stock_entry.custom_available_qty = available_qty_total

    stock_entry.custom_difference_qty = difference_qty

    stock_entry.custom_fully_available = fully_available

    stock_entry.custom_partially_available = partially_available
    # ❌ NO ITEMS
    if not stock_entry.items:
        frappe.throw("No stock available for selected Material Requests")

    stock_entry.insert()

    return stock_entry.name

