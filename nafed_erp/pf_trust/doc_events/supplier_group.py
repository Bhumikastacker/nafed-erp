import frappe
from frappe import _

def validate(doc, method=None):
    if doc.custom_is_society:
        existing = frappe.db.exists(
            "Supplier Group",
            {
                "custom_is_society": 1,
                "name": ["!=", doc.name]
            }
        )

        if existing:
            frappe.throw(
                _("Only one Supplier Group can have 'Is Society' enabled. Already set in: {0}")
                .format(existing)
            )