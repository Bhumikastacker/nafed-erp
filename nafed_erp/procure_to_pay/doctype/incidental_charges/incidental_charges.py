# Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
class IncidentalCharges(Document):

    def validate(self):
        # Mandatory fields
        if not self.charge_type or not self.calculation_type:
            frappe.throw("Charge Type and Calculation Type required")

        # Date validation
        if self.effective_from and self.effective_to:
            if self.effective_from > self.effective_to:
                frappe.throw("Invalid date range")

        # Overlapping validation
        existing = frappe.db.sql("""
            SELECT name FROM `tabIncidental Charges`
            WHERE charge_type=%s
            AND name != %s
            AND (
                (%s BETWEEN effective_from AND effective_to)
                OR (%s BETWEEN effective_from AND effective_to)
            )
        """, (self.charge_type, self.name, self.effective_from, self.effective_to))

        if existing:
            frappe.throw("Overlapping charge configuration exists")

def before_save(self):
    if not self.version:
        self.version = "v1.0"
    else:
        v = float(self.version.replace("v", ""))
        self.version = f"v{v+0.1:.1f}"