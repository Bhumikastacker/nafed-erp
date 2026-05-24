# Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class LegalCaseCourtOrder(Document):
    def validate(self):
        if not self.order_document:
            frappe.throw("Court order document is mandatory")
