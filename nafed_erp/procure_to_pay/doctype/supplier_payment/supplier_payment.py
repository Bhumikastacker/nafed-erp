# Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
def validate(self):

    if self.amount_paid < 0:
        frappe.throw("Amount Paid cannot be negative")

    if self.amount_paid > self.total_payable:
        frappe.throw("Paid amount cannot exceed payable amount")

class SupplierPayment(Document):
	pass
