import frappe

def update_payment_entry_id(doc, method):
    prb_id = doc.get("custom_payment_request_branch")
    prb_status = frappe.db.get_value("Branch Payment Request", prb_id, "status")

    print("******************************************************************************")
    print(prb_status)

    if not prb_id:
        return
    if prb_status =="Approved":
        frappe.db.set_value("Branch Payment Request",prb_id,"payment_entry_id",doc.name)
    if prb_status=="Fund Released":
        frappe.db.set_value("Branch Payment Request",prb_id,"fund_recevied_entry_id",doc.name)
    frappe.db.commit()


