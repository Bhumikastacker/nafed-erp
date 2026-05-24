# Copyright (c) 2025, CSM Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _

class MemberType(Document):
	
	def validate(self):
		if self.short_code:

			existing = frappe.db.exists(
				self.doctype,
				{
					"short_code": self.short_code,
					"name": ["!=", self.name]
				}
			)
			print("sssssssssssssssssssssssssssssss", existing)
			if existing:
				frappe.throw(_("Member Type Code already exists."))
