# Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import date_diff, today,getdate
from frappe.utils import flt
from frappe.model.document import Document


class ProjectExtensionRequest(Document):

	def validate(self):
		self.validate_dates()
		self.validate_project_fields()

	def on_update(self):
		if self.workflow_state == "Approved":
			self.extend_project()

	def extend_project(self):
		project = frappe.get_doc("Project", self.project)

		project.expected_end_date=self.project_new_end_date
		if self.additional_cost: 
			project.estimated_costing+=self.additional_cost
		project.save(ignore_permissions=True)

	def validate_dates(self):
		old_end_date = getdate(self.project_old_end_date)
		new_end_date = getdate(self.project_new_end_date)
		if date_diff(old_end_date, today()) > 90:
			frappe.throw("Extension allowed only within 90 days of project end date")

		if new_end_date <= old_end_date:
			frappe.throw("New end date must be after old end date")

	def validate_project_fields(self):

		if not self.project:
			frappe.throw("Project is required.")

		project = frappe.get_doc("Project", self.project)

		# -----------------------------------------
		# Status must be Open
		# -----------------------------------------
		if project.status != "Open":
			frappe.throw("Project must be in 'Open' status.")

		# -----------------------------------------
		# Percent Complete must not be 0
		# -----------------------------------------
		if not (0 < flt(project.percent_complete) < 100):
			frappe.throw("Project percent complete must be between 0 and 100.")

		# -----------------------------------------
		# Approval Status must be Approved
		# -----------------------------------------
		if project.custom_approval_status != "Approved":
			frappe.throw("Project must be Approved.")

		# -----------------------------------------
		# Project must be Active
		# -----------------------------------------
		if project.is_active != "Yes":
			frappe.throw("Project must be Active.")