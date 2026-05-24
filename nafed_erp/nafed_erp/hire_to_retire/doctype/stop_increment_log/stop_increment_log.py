# Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class StopIncrementLog(Document):
	def validate(self):
		if self.employee:

			# 🔥 Get employee details
			emp = frappe.db.get_value(
				"Employee",
				self.employee,
				["company", "status"],
				as_dict=True
			)

			if not emp:
				frappe.throw("Invalid Employee selected")

			# ❌ Company mismatch
			if self.company and emp.company != self.company:
				frappe.throw(
					f"Employee <b>{self.employee}</b> does not belong to Company <b>{self.company}</b>"
				)

			# ❌ Inactive employee
			if emp.status != "Active":
				frappe.throw(
					f"Employee <b>{self.employee}</b> is not Active"
				)