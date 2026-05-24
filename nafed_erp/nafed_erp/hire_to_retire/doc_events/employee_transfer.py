import frappe
from frappe import _
from frappe.utils import getdate

def validate_transfer_date(doc, method):
    date_of_joining = frappe.db.get_value("Employee", doc.employee, "date_of_joining")
    
    if getdate(doc.transfer_date) < getdate(date_of_joining):
        frappe.throw(
                    _("Transfer Date ({0}) cannot be earlier than Employee's Joining Date ({1}).")
                    .format(doc.transfer_date, date_of_joining)
                )