# Copyright (c) 2025, CSM Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class PropertyFinancialExpenditures(Document):
	def after_insert(self):
    		self.create_property_expenditure_log()

	def create_property_expenditure_log(self):
        	property_doc = frappe.get_doc('Property', self.property_id)
	        log_entry = {
	            'expenditure_id': self,
	            'expense_category': self.expense_category,
	            'vendor': self.vendor,
	            'amount_payable':self.amount_payable,
	            'amount_paid': self.amount_paid,
	            'penaltyinterest': self.penaltyinterest
	        }
	        property_doc.append('property_expenditure_log', log_entry)
	        property_doc.save()
