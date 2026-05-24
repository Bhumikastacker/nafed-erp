# Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _

class MeetingType(Document):

	def validate(self):
		if self.code:

			existing = frappe.db.exists(
				self.doctype,
				{
					"code": self.code,
					"name": ["!=", self.name]
				}
			)
			print("sssssssssssssssssssssssssssssss", existing)
			if existing:
				frappe.throw(_("Meeting Type Code already exists."))
