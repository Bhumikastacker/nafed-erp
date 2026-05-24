# Copyright (c) 2025, CSM Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class PropertyTaxandCompliances(Document):
	def after_insert(self):
    		self.create_property_tax_log()

	def create_property_tax_log(self):
        	property_doc = frappe.get_doc('Property', self.property_id)
	        log_entry = {
	            'property_tax_id': self,
	            'compliance_type': self.compliance_type,
	            'assessment_year': self.assessment_year,
	            'tax_amount':self.tax_amount,
	            'due_date': self.due_date
	        }
	        property_doc.append('property_tax_log', log_entry)
	        property_doc.save()
