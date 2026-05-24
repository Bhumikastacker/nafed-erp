# Copyright (c) 2025, CSM Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

from frappe.model.document import Document
from frappe.utils import add_days, today
from frappe.utils.data import date_diff

class RecordFixedDepositDetails(Document):
    def validate(self):
        """Called automatically before saving/submitting the document"""
        self.validate_interest_rate()

    def validate_interest_rate(self):
        if self.annual_interest_rate is None:
            frappe.throw("Please enter a valid annual interest rate.")
        
        # Ensure the value is numeric
        try:
            rate = float(self.annual_interest_rate)
        except ValueError:
            frappe.throw("Annual Interest Rate must be a numeric value.")
        
        if not (0.01 <= rate <= 20):
            frappe.throw("Annual Interest Rate must be between 0.01% and 20%")
            
			
 # your normal Document logic stays here

# def send_maturity_alerts():
#     """Send alerts 30, 15, 7 days before maturity."""
#     records = frappe.get_all(
#         "Record Fixed Deposit Details",
#         fields=["name", "bank_name", "maturity_date", "owner"],
#         filters={"docstatus": 1}  # submitted
#     )

#     for rec in records:
#         if not rec.maturity_date:
#             continue

#         days_left = date_diff(rec.maturity_date, today())

#         if days_left in [30, 15, 7]:
#             create_notification(rec, days_left)

# def create_notification(rec, days_left):
#     """Create a notification log + optional email."""
#     message = (
#         f"Your Fixed Deposit with **{rec.bank_name}** "
#         f"is maturing in **{days_left} days**.<br>"
#         f"FD Record: <b>{rec.name}</b>"
#     )

#     # Create In-App Notification
#     notif = frappe.get_doc({
#         "doctype": "Notification Log",
#         "subject": f"FD Maturity Alert – {days_left} days left",
#         "email_content": message,
#         "for_user": rec.owner,
#         "document_type": "Record Fixed Deposit Details",
#         "document_name": rec.name,
#         "type": "Alert"
#     }).insert(ignore_permissions=True)

#     print(f"Notification created for {rec.name}, {days_left} days left")  # ✅ testing

#     # Temporarily comment out email
#     # frappe.sendmail(
#     #     recipients=[rec.owner],
#     #     subject=f"FD Maturity Alert – {days_left} days remaining",
#     #     message=message
#     # )


 