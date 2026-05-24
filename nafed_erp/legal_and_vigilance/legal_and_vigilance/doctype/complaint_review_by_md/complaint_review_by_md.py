# Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ComplaintReviewbyMD(Document):
	pass



@frappe.whitelist()
def create_verification_routing(complaint_review_id):
    # Prevent duplicate routing
    existing = frappe.db.exists(
        "Verification Routing",
        {"ref": complaint_review_id}
    )
    if existing:
        frappe.throw("Verification Routing already exists for this Complaint Review")

    review = frappe.get_doc("Complaint Review by MD", complaint_review_id)

    vr = frappe.new_doc("Verification Routing")
    vr.ref = review.name
    vr.complaint_receipt_id = review.complaint_id
    vr.assigned_department = review.assigned_officer__department
    vr.task_status = "Pending"

    vr.insert(ignore_permissions=True)
    frappe.db.commit()

    return vr.name

