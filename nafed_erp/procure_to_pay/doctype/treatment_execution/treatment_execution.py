# Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class TreatmentExecution(Document):

    def on_submit(self):

        # Validate Schedule Reference
        if not self.schedule_reference:
            frappe.throw("Schedule Reference is mandatory")

        # Update Fumigation Schedule
        frappe.db.set_value(
            "Fumigation Schedule",
            self.schedule_reference,
            {
                "schedule_status": "Completed",
                "next_due_date": self.next_due_date
            }
        )

        frappe.msgprint(
            "Fumigation Schedule updated successfully"
        )