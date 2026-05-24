import frappe

def update_jwo_invoice_status(doc, method):

    if not doc.custom_jute_work_order:
        return

    jwo_name = doc.custom_jute_work_order

    if not frappe.db.exists("Jute Work Order", jwo_name):
        return

    jwo = frappe.get_doc("Jute Work Order", jwo_name)

    if jwo.status == "Invoice Created":
        return

    jwo.status = "Invoice Created"
    jwo.ref = doc.name
    jwo.save(ignore_permissions=True)