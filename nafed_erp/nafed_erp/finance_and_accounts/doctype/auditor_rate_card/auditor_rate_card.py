# Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class AuditorRateCard(Document):
	def validate(self):
		if self.rate and self.rate > 1000000:
			frappe.throw("Rate cannot be greater than ₹10,00,000")
