# Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class DispatchDetails(Document):
    pass







def update_jwo_dispatch_status(doc, method):

    if not doc.work_order_ref_no:
        return

    if not frappe.db.exists("Jute Work Order", doc.work_order_ref_no):
        return

    jwo = frappe.get_doc("Jute Work Order", doc.work_order_ref_no)

    # Avoid overwrite
    if jwo.status == "Dispatch Created":
        return

    jwo.status = "Dispatch Created"
    jwo.save(ignore_permissions=True)