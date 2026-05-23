# Copyright (c) 2025, CSM Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _


class LawCode(Document):

	def validate(self):
		if self.code:

			existing = frappe.db.exists(
				self.doctype,
				{
					"code": self.code,
					"name": ["!=", self.name]
				}
			)
			if existing:
				frappe.throw(_("By Law Code already exists."))
