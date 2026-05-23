# Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class LegalCaseHearingDocument(Document):
	def before_insert(self):
		self.uploaded_by = frappe.session.user
		self.uploaded_on = now()