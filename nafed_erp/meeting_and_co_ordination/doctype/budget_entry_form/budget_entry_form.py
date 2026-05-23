# Copyright (c) 2025, CSM Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import date

class BudgetEntryForm(Document):
	

	def validate(self):
		self.validate_duplicate_estimated()
		for df in self.meta.fields:
			# Check only numeric fields
			if df.fieldtype in ("Int", "Float", "Currency", "Percent"):
				value = self.get(df.fieldname)

				if value is not None and value < 0 and not df.label == "Profit":
					frappe.throw(
						_("{0} cannot be less than zero").format(df.label)
					)
					
	def validate_duplicate_estimated(self):
		if not self.estimated_budget_form_id:
			return

		existing = frappe.db.exists(
			self.doctype,
			{
				"estimated_budget_form_id": self.estimated_budget_form_id,
				"name": ["!=", self.name]  # important for edit case
			}
		)

		if existing:
			frappe.throw(
				f"A Actual Budget Entry Form is already submitted forestimation {self.estimated_budget_form_id}   with Reference number {existing}"
			)

		

	def on_update(self):
		self.log_workflow_action()

	def log_workflow_action(self):
		before = self.get_doc_before_save()
		if not before:
			return

		if before.workflow_state == self.workflow_state:
			return
		print("ssssssssssssssssssss",self.workflow_state)
		if self.workflow_state in ("Send To Division Head",  "Coordination Division","Sent To MD",
							 "Approved",
							"Rejected", "Cancel", "Draft") and not self.remarks:
			frappe.throw("Remarks are mandatory for this action.")

		idx = frappe.db.count(
			"Hire To Retire Logs",
			{
			"parent": self.name,
			"parenttype": "Budget Entry Form",
			"parentfield": "act_logs"
			}
			) + 1

		frappe.get_doc({
			"doctype": "Hire To Retire Logs",
			"parent": self.name,
			"parenttype": "Budget Entry Form",
			"parentfield": "act_logs",
			"idx": idx,

			"doc_name": self.name,
			"state":  self.workflow_state,
			"action_taken_by": frappe.session.user,
			"action_taken_on": frappe.utils.now(),
			"remarks": self.remarks
			}).insert(ignore_permissions=True)

		self.db_set("remarks", None, update_modified=False)
		self.reload()
	
