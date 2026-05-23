import frappe
from frappe.utils.background_jobs import enqueue

def purchase_receipt_on_submit_all(doc, method):
    purchase_receipt_on_submit(doc, method)
    update_dispatch_receipt_status(doc, method)
    # create_purchase_invoice_from_pr(doc, method)

def purchase_receipt_on_submit(doc, method):
    sales_orders = set()

    # 1️⃣ Collect all linked Sales Orders
    for item in doc.items:
        if item.sales_order:
            sales_orders.add(item.sales_order)

    # 2️⃣ Process each Sales Order
    for so_name in sales_orders:
        so = frappe.get_doc("Sales Order", so_name)

        all_available = True

        for so_item in so.items:

            # Get actual stock from Bin
            actual_qty = frappe.db.get_value(
                "Bin",
                {
                    "item_code": so_item.item_code,
                    "warehouse": so_item.warehouse
                },
                "actual_qty"
            ) or 0

            if actual_qty < so_item.qty:
                all_available = False
                break

        # 3️⃣ Update flag if all items available
        if all_available:
            frappe.db.set_value(
                "Sales Order",
                so_name,
                "custom_ready_for_delivery",
                1
            )



def update_dispatch_receipt_status(doc, method):
    if not doc.custom_whr_no:
        return

    # Dispatch Receipt find karo
    dispatch = frappe.db.get_value(
        "Dispatch Receipt",
        {"name": doc.custom_whr_no},
        ["name", "status"],
        as_dict=1
    )

    if not dispatch:
        return

    # Agar already completed hai to skip
    if dispatch.status == "Receipt Completed":
        return

    # Update Dispatch Receipt
    frappe.db.set_value("Dispatch Receipt", dispatch.name, {
        "status": "Receipt Completed",
        "receipt_id": doc.name
    })

    frappe.db.commit()

# def create_purchase_invoice_from_pr(doc, method):

#     # Purchase Invoice create karo
#     pi = frappe.new_doc("Purchase Invoice")

#     # Parent Fields Mapping
#     pi.supplier = doc.supplier
#     pi.company = doc.company
#     pi.posting_date = doc.posting_date
#     pi.set_posting_time = 1
#     pi.posting_time = doc.posting_time
#     pi.currency = doc.currency
#     pi.division = doc.division

#     # Items Mapping
#     for item in doc.items:
#         pi.append("items", {
#             "item_code": item.item_code,
#             "item_name": item.item_name,
#             "qty": item.qty,
#             "rate": item.rate,
#             "amount": item.amount,
#             "warehouse": item.warehouse,
#             "purchase_receipt": doc.name,
#             "pr_detail": item.name
#         })

#     # Save and Submit
#     pi.insert(ignore_permissions=True)
#     pi.submit()

#     frappe.msgprint(f"Purchase Invoice {pi.name} created successfully.")



@frappe.whitelist()
def get_barcode_details(barcode):
    result = frappe.db.get_value(
        "Item Barcode",
        {"barcode": barcode},
        ["parent", "custom_mrp"],
        as_dict=True
    )

    return result

def update_batch_expiry_from_pr(doc, method):
    
    enqueue(
        "nafed_erp.admin.doc_events.purchase_receipt.process_batch_expiry_update",
        queue="long",   # use long since this can be heavy
        timeout=800,
        doc_name=doc.name
    )

def process_batch_expiry_update(doc_name):

    doc = frappe.get_doc("Purchase Receipt", doc_name)
   
    for row in doc.items:

        if not row.serial_and_batch_bundle:
            continue

        if not row.custom_expiry_date:
            continue

        try:
            bundle = frappe.get_doc(
                "Serial and Batch Bundle",
                row.serial_and_batch_bundle
            )

            updated_batches = set()

            for entry in bundle.entries:

                if not entry.batch_no or entry.batch_no in updated_batches:
                    continue

                current_expiry = frappe.db.get_value(
                    "Batch",
                    entry.batch_no,
                    "expiry_date"
                )
                if not current_expiry or current_expiry != row.custom_expiry_date:
                    frappe.db.set_value(
                        "Batch",
                        entry.batch_no,
                        "expiry_date",
                        row.custom_expiry_date
                    )
                    frappe.db.commit()

                updated_batches.add(entry.batch_no)

        except Exception as e:
            frappe.log_error(
                title="Batch Expiry Update Failed (Background Job)",
                message=f"""
                PR: {doc.name}
                Item Row: {row.idx}
                Bundle: {row.serial_and_batch_bundle}
                Error: {str(e)}
                """
            )

import frappe


@frappe.whitelist()
def get_purchase_receipt_stats(purchase_receipt):

    lot_receipt = frappe.db.count(
        "Lot Receipt",
        {"purchase_receipt": purchase_receipt}
    )

    qi_pending = frappe.db.count(
        "Quality Inspection",
        {
            "reference_name": purchase_receipt,
            "status": ["!=", "Accepted"]
        }
    )

    grn_pending = frappe.db.count(
        "Goods Receipt Notes",
        {
            "purchase_receipt": purchase_receipt,
            "docstatus": 0
        }
    )

    pi_pending = frappe.db.count(
        "Purchase Invoice",
        {
            "purchase_receipt": purchase_receipt,
            "docstatus": 0
        }
    )

    return {
        "lot_receipt": lot_receipt,
        "qi_pending": qi_pending,
        "grn_pending": grn_pending,
        "pi_pending": pi_pending
    }