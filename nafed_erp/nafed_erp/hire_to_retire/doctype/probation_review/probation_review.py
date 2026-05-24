# Copyright (c) 2025, CSM Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ProbationReview(Document):
	def on_update_after_submit(doc):
		if doc.recommendation == "Extended" and doc.workflow_state == "Probation Confirmed":
			employee = frappe.get_doc("Employee", doc.employee_id)
			employee.custom_ppedate = doc.extension_duration
			employee.save(ignore_permissions=True)