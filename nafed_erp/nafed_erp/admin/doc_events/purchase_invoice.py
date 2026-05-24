import frappe

def update_dispatch_receipt_invoice(doc, method):
    if not doc.get("custom_whr_no"):
        return

    dispatch_name = doc.get("custom_whr_no")

    # Dispatch Receipt fetch
    dispatch = frappe.db.get_value(
        "Dispatch Receipt",
        {"name": dispatch_name},
        ["name", "status"],
        as_dict=1
    )

    if not dispatch:
        return

    if dispatch.status == "Invoice Completed":
        return

    # Update Dispatch Receipt
    frappe.db.set_value("Dispatch Receipt", dispatch.name, {
        "status": "Invoice Completed",
        "invoice_id": doc.name
    })

    frappe.db.commit()
