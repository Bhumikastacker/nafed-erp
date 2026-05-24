import frappe
from frappe.model.document import Document


class NomineeForm(Document):

    def validate(self):

        if self.membership_id:
            existing = frappe.db.exists(
                "Nominee  Form",
                {
                    "membership_id": self.membership_id,
                    "name": ["!=", self.name]
                }
            )

            if existing:
                frappe.throw("Nominee Form is already submitted for this Membership ID.")

    def after_insert(self):

        if self.membership_id:
            frappe.db.set_value(
                "Board Members",
                self.membership_id,
                "custom_is_nominee_submitted",
                1
            )