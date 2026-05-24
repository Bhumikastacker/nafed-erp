import frappe

def disable_supplier(doc, method):
    if doc.workflow_state == "Pending Approval":
        doc.disabled = 1
        doc.save()