# Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Lot(Document):
	def after_insert(self):
		self.lot_id = self.name
		self.save()
		
		
		
