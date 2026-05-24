# Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import now

from frappe.model.document import Document


class ComplaintReceipt(Document):
	pass
@frappe.whitelist()
def create_md_review(complaint_id):
    # Fetch Complaint Receipt
    complaint = frappe.get_doc("Complaint Receipt", complaint_id)

    # Prevent duplicate MD Review
    existing = frappe.db.exists(
        "Complaint Review by MD",
        {"complaint_id": complaint.name}
    )
    if existing:
        frappe.throw(
            f"Complaint Review by MD already exists: <b>{existing}</b>"
        )

    # Create MD Review
    review = frappe.new_doc("Complaint Review by MD")
    review.complaint_id = complaint.name
    review.review_timestamp = now()

    # Optional mappings (add if needed later)
    # review.remarks = complaint.description

    review.insert(ignore_permissions=True)

    return review.name
