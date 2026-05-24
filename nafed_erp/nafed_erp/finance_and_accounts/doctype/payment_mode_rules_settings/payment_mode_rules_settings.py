# Copyright (c) 2025, CSM Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class PaymentModeRulesSettings(Document):

    def validate(self):
        self.validate_duplicate_range()

    def validate_duplicate_range(self):
        # Fetch existing rules for same party_type & mode_of_payment
        existing_rules = frappe.db.get_list(
            "Payment Mode Rules Settings",
            filters={
                "party_type": self.party_type,
                "mode_of_payment": self.mode_of_payment,
                "name": ["!=", self.name]  # exclude current
            },
            fields=["name", "minimum_amount", "maximum_amount"]
        )

        for rule in existing_rules:
            # Check for overlapping ranges
            if (
                float(self.minimum_amount) <= float(rule["maximum_amount"])
                and float(self.maximum_amount) >= float(rule["minimum_amount"])
            ):
                frappe.throw(
                    f"""
                    Overlapping Rule Detected for <b>{self.party_type}</b> and 
                    <b>{self.mode_of_payment}</b>.<br><br>
                    Existing Rule: <b>{rule['name']}</b><br>
                    Range: {rule['minimum_amount']} to {rule['maximum_amount']}<br><br>
                    You cannot create overlapping ranges for the same party type 
                    and mode of payment.
                    """
                )


@frappe.whitelist()
def get_payment_mode(amount, party_type=None):
    amount = float(amount)

    if not party_type:
        return None

    # Fetch rules matching party type and amount
    rules = frappe.db.get_list(
        "Payment Mode Rules Settings",
        filters={
            "is_active": 1,
            "party_type": party_type,
            "minimum_amount": ["<=", amount],
            "maximum_amount": [">=", amount]
        },
        fields=[
            "minimum_amount",
            "maximum_amount",
            "mode_of_payment",
            "party_type"
        ]
    )

    if not rules:
        return None

    # No need to sort because all rules already have party_type
    return rules[0]
