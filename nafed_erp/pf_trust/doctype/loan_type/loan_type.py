# Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _

class LoanType(Document):
	def validate(self):
		self.validate_no_duplicate_housing_rules()

	def validate_no_duplicate_housing_rules(self):
		seen = set()

		for row in self.housing_rules:
			key = row.sub_category  # change to your actual fieldname

			if key in seen:
				frappe.throw(
					_("Duplicate Housing Rule found for: {0}").format(key)
				)

			seen.add(key)
