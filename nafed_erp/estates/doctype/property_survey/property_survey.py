# Copyright (c) 2025, CSM Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class PropertySurvey(Document):
	def after_insert(self):
    		self.create_property_survey_log()

	def create_property_survey_log(self):
        	property_doc = frappe.get_doc('Property', self.property_id)
	        log_entry = {
	            'survey_id': self,
	            'survey_date': self.survey_date,
	            'surveyor_name': self.surveyor_name,
	            'survey_type':self.survey_type
	        }
	        property_doc.append('survey_history_log', log_entry)
	        property_doc.save()
