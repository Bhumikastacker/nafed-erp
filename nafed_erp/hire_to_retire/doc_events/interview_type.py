import frappe
import re
from frappe import _

# ===========================================================
# Interview Type name should only contain letters and spaces 
# Numbers and Special characters are not allowed
# ===========================================================

def validate_interview_type_name(doc, method=None, olddn=None, newdn=None):
    name_to_check = newdn if newdn else doc.name
    
    if name_to_check:
        if not re.match("^[a-zA-Z\s]+$", name_to_check):
            frappe.throw(_("Interview Type name '{0}' is invalid.").format(name_to_check))