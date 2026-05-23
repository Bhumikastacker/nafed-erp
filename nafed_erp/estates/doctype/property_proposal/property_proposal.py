# Copyright (c) 2025, CSM Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class PropertyProposal(Document):
	def on_update(self):
		if self.workflow_state == "Draft":
			self.db_set("status", "Draft")
		elif self.workflow_state == "Submitted":
			self.db_set("status", "Submitted")
		elif self.workflow_state == "Send for HO Approval":
			self.db_set("status", "Send for HO Approval")
		elif self.workflow_state == "Send for MD Approval":
			self.db_set("status", "Send for MD Approval")
		elif self.workflow_state == "Rejected":
			self.db_set("status", "Rejected")
		elif self.workflow_state == "Approved":
			self.db_set("status", "Approved")
			print(self.property_name)
			new_property = frappe.get_doc({
			"doctype": "Property",
            "property_name": self.property_name,
			"zone":self.zone,
			"branch":self.branch
			})
			new_property.insert(ignore_permissions=True) 
			frappe.db.commit()

			frappe.msgprint(f"Property record created for {self.property_name}")

