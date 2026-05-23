# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# # For license information, please see license.txt

# import frappe
# from frappe import _
# from frappe.model.document import Document
# from frappe.model.mapper import get_mapped_doc
# from  hrms.hr.doctype.job_requisition.job_requisition import JobRequisition

# class CustomJobRequisition(JobRequisition):
	
# 	print("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
# 	def on_update(self):
# 		self.log_workflow_action()
	

# 	def log_workflow_action(self):
# 		before = self.get_doc_before_save()
# 		if not before:
# 			return

# 		if before.workflow_state == self.workflow_state:
# 			return
# 		print("ssssssssssssssssssss",self.workflow_state)
# 		if self.workflow_state in ("Pending for Approval","Send Back for Rework","Approved","Cancelled","Re-Submit For Approval") and not self.custom_remarks:
# 			frappe.throw("remarks are mandatory for this action.")

# 		idx = frappe.db.count(
# 			"Hire To Retire Logs",
# 			{
# 				"parent": self.name,
# 				"parenttype": "Job Requisition",
# 				"parentfield": "custom_hire_to_retire_logs"
# 			}
# 		) + 1

# 		frappe.get_doc({
# 			"doctype": "Hire To Retire Logs",
# 			"parent": self.name,
# 			"parenttype": "Job Requisition",
# 			"parentfield": "custom_hire_to_retire_logs",
# 			"idx": idx,

# 			"doc_name": self.name,
# 			"state": self.workflow_state,
# 			"action_taken_by": frappe.session.user,
# 			"action_taken_on": frappe.utils.now(),
# 			"custom_remarks": self.custom_remarks
# 		}).insert(ignore_permissions=True)

# 		self.db_set("custom_remarks", None, update_modified=False)
# 		self.reload()
