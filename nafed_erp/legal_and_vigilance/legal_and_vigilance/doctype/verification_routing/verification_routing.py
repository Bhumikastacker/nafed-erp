# Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class VerificationRouting(Document):
	def after_insert(self):
		self.task_id = self.name

@frappe.whitelist()
def create_verification_reporting(verification_routing_id):
    vr = frappe.get_doc("Verification Routing", verification_routing_id)

    # Optional: prevent duplicate creation
    existing = frappe.db.exists(
        "Verification Reporting",
        {"ref": verification_routing_id}
    )
    if existing:
        frappe.throw("Verification Reporting already exists for this record")

    doc = frappe.new_doc("Verification Reporting")
    
    # 🔑 CRITICAL LINK
    doc.ref = verification_routing_id
    
    # Optional field mappings
    doc.complaint_receipt_id = vr.complaint_receipt_id
    doc.generated_by = frappe.session.user
    
    doc.insert(ignore_permissions=True)

    return doc.name
