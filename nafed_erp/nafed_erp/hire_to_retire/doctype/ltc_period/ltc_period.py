# Copyright (c) 2025, CSM Technologies Pvt Ltd and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
from frappe.utils import getdate

class LTCPeriod(Document):
	def validate(self):
		self.set_year_slab()

	def set_year_slab(self):
		"""Generate year slab based on period_start and period_end (e.g., 2023-2025)."""

		if not self.period_start or not self.period_end:
			return

		start_year = getdate(self.period_start).year
		end_year = getdate(self.period_end).year

		# Create slab like "2023-2025"
		self.year_slab = f"{start_year}-{end_year}"
