# Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class MomFromDivision(Document):
	
	def on_update(self):
		if not self.mom_no:
			return

		division_list = frappe.get_all(
			"Mom From Division",
			filters={"mom_no": self.mom_no},
			pluck="division"
		)

		filters = {"doc_type": "Mom"}

		if division_list:
			filters["division"] = ["not in", division_list]

		remaining = frappe.db.exists("Mails Configurations", filters)

		frappe.db.set_value(
			"Meeting MoM",
			self.mom_no,
			"check_mom_from_div",
			0 if remaining else 1
		)
