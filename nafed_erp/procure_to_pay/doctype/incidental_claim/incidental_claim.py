# Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
# For license information, please see license.txt
import frappe
from frappe.model.document import Document
class IncidentalClaim(Document):
    pass 
#     def validate(self):
#         total = 0
#         tax_total = 0
#         paid = self.paid_amount or 0

#         for row in self.items:

#             charge = frappe.get_doc("Incidental Charges", row.charge_type)

#             rate = charge.rate
#             row.rate = rate

#             # Calculation
#             if self.claim_type == "Storage":
#                 row.amount = (row.quantity or 0) * (row.days or 0) * rate
#             else:
#                 row.amount = (row.quantity or 0) * rate

#             total += row.amount

#             tax_total += (row.amount * (charge.tax or 0)) / 100

#         self.total_amount = total
#         self.tax_amount = tax_total
#         self.net_payable = total + tax_total
#         self.outstanding_amount = self.net_payable - paid

# def before_submit(self):
#     if frappe.db.exists("Incidental Claim", {
#         "sla": self.sla,
#         "procurement_period": self.procurement_period,
#         "name": ["!=", self.name]
#     }):
#         frappe.msgprint("Script Triggered")
#         frappe.throw("Duplicate claim detected")
#     if not doc.incidental_claim:
#         frappe.msgprint("No Claim Linked")
#         return
    

# def on_submit(self):
#     # Field name on Payment Entry is custom_incidental_claim
#     claim_id = self.get('custom_incidental_claim') or self.get('incidental_claim')
#     if not claim_id:
#         return

#     claim = frappe.get_doc('Incidental Claim', claim_id)
#     paid = self.paid_amount or 0

#     if paid <= 0:
#         frappe.throw('Paid amount must be greater than 0')

#     outstanding = claim.outstanding_amount or claim.net_payable or 0
#     if paid > outstanding:
#         frappe.throw('Payment exceeds outstanding amount')

#     new_paid = (claim.paid_amount or 0) + paid
#     new_outstanding = (claim.net_payable or 0) - new_paid

#     if new_outstanding <= 0:
#         new_outstanding = 0
#         new_status = 'Paid'
#     else:
#         new_status = 'Partially Paid'

#     claim.db_set('paid_amount', new_paid, update_modified=False)
#     claim.db_set('outstanding_amount', new_outstanding, update_modified=False)
#     claim.db_set('payment_status', new_status, update_modified=False)
#     frappe.db.commit()

#     frappe.msgprint(
#         f'Incidental Claim {claim_id} updated. Status: {new_status}. Outstanding: {new_outstanding}',
#         indicator='green'
#     )
    
    # def on_payment_submit(doc, method=None):
    #     claim_id = doc.get('custom_incidental_claim')
    #     if not claim_id:
    #         return
    #     claim = frappe.get_doc('Incidental Claim', claim_id)
    #     paid = doc.paid_amount or 0
    #     if paid <= 0:
    #         frappe.throw('Paid amount must be greater than 0')
    #     outstanding = claim.outstanding_amount or claim.net_payable or 0
    #     if paid > outstanding:
    #         frappe.throw('Payment exceeds outstanding amount')
    #     new_paid = (claim.paid_amount or 0) + paid
    #     new_outstanding = (claim.net_payable or 0) - new_paid
    #     if new_outstanding <= 0:
    #         new_outstanding = 0
    #         new_status = 'Paid'
    #     else:
    #         new_status = 'Partially Paid'
    #     claim.db_set('paid_amount', new_paid, update_modified=False)
    #     claim.db_set('outstanding_amount', new_outstanding, update_modified=False)
    #     claim.db_set('payment_status', new_status, update_modified=False)
    #     frappe.db.commit()
    #     frappe.msgprint(
    #         f'Incidental Claim {claim_id} updated. Status: {new_status}. Outstanding: {new_outstanding}',
    #         indicator='green'
    #     )


    # def on_payment_cancel(doc, method=None):
    #     claim_id = doc.get('custom_incidental_claim')
    #     if not claim_id:
    #         return
    #     claim = frappe.get_doc('Incidental Claim', claim_id)
    #     paid = doc.paid_amount or 0
    #     new_paid = max((claim.paid_amount or 0) - paid, 0)
    #     new_outstanding = (claim.net_payable or 0) - new_paid
    #     new_status = 'Paid' if new_outstanding <= 0 else ('Partially Paid' if new_paid > 0 else 'Unpaid')
    #     claim.db_set('paid_amount', new_paid, update_modified=False)
    #     claim.db_set('outstanding_amount', new_outstanding, update_modified=False)
    #     claim.db_set('payment_status', new_status, update_modified=False)
    #     frappe.db.commit()