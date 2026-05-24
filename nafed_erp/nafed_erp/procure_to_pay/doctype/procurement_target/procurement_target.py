# Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ProcurementTarget(Document):

    def validate(self):
        self.calculate_total()

    def before_save(self):
        self.calculate_total()

    def calculate_total(self):
        total = 0

        for row in self.commodity_details:
            total += row.target_quantity or 0

        self.total_allocated_qty = total
