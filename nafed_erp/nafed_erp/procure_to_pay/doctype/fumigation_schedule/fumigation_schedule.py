from frappe.model.document import Document
import frappe
from frappe.utils import (
    getdate,
    today,
    add_days,
    add_months
)

class FumigationSchedule(Document):

    def validate(self):

        # Mandatory Warehouse Validation
        if not self.warehouse:
            frappe.throw("Warehouse is mandatory")

        # Scheduled Date Validation
        if (
            self.scheduled_date
            and getdate(self.scheduled_date) < getdate(today())
        ):
            frappe.throw("Scheduled Date cannot be in past")

        # Set Next Due Date
        self.set_next_due_date()

    def set_next_due_date(self):

        if not self.scheduled_date:
            return

        frequency = (self.frequency or "").strip().lower()

        # Weekly
        if frequency == "weekly":

            self.next_due_date = add_days(
                self.scheduled_date,
                7
            )

        # Monthly
        elif frequency == "monthly":

            self.next_due_date = add_months(
                self.scheduled_date,
                1
            )

        # Quarterly
        elif frequency == "quarterly":

            self.next_due_date = add_months(
                self.scheduled_date,
                3
            )

        # One-time
        elif frequency in ["one-time", "one time"]:

            self.next_due_date = self.scheduled_date

    def on_update(self):

        # Prevent next_due_date from becoming empty
        if not self.next_due_date:

            self.set_next_due_date()

            frappe.db.set_value(
                self.doctype,
                self.name,
                "next_due_date",
                self.next_due_date,
                update_modified=False
            )