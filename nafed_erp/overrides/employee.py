import frappe
from frappe import _
import re

def validate_employee_name(doc, method):
    """Validate first name and last name for special characters"""
    
    # Special characters regex
    special_char_pattern = r'[!@#$%^&*()_+\=\[\]{};:"\\|,.<>\/?]+'
    
    # Validate First Name
    if doc.first_name:
        if re.search(special_char_pattern, doc.first_name):
            frappe.throw(_("First Name cannot contain special characters: {0}").format(doc.first_name))
    
    # Validate Last Name (if provided)
    if doc.last_name:
        if re.search(special_char_pattern, doc.last_name):
            frappe.throw(_("Last Name cannot contain special characters: {0}").format(doc.last_name))