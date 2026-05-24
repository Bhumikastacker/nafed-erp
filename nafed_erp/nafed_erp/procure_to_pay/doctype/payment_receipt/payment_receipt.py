# Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
def validate(self):

    if self.amount_received < 0:
        frappe.throw("Amount cannot be negative")

    if self.amount_received > self.total_receivable:
        frappe.throw("Received amount cannot exceed total receivable")

class PaymentReceipt(Document):
	pass

def validate(self):

    if not self.payment_receipt:
        frappe.throw("Payment Receipt is mandatory")

    existing = frappe.db.exists(
        "Subsidy Claim",
        {
            "lot_id": self.lot_id,
            "docstatus": ["!=", 2]
        }
    )

    if existing and existing != self.name:
        frappe.throw("Subsidy already claimed for this Lot")
