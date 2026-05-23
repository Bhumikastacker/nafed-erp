# Copyright (c) 2025, Digitalis Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class PolicyManagement(Document):
	def on_update(self):
		if self.workflow_state == "Draft":
			self.db_set("status", "Draft")
		if self.workflow_state == "Submitted":
			self.db_set("status", "Submitted")
		if self.workflow_state == "Reviewed":
			self.db_set("status", "Reviewed")	
		if self.workflow_state == "Approved":
			self.db_set("status", "Approved")
		if self.workflow_state == "Rejected":
			self.db_set("status", "Rejected")
