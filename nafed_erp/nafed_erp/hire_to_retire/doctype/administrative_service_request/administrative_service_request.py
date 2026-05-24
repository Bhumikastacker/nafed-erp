# Copyright (c) 2025, CSM Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import nowdate


class AdministrativeServiceRequest(Document):
	def on_submit(self):
        # save the value in database
		self.db_set("submission_date", nowdate())

