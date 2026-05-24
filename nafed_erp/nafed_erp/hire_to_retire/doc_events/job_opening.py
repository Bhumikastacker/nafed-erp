import frappe
from frappe import _
from frappe.utils import flt

def validate(doc, method):

    # ================= Age Validation =================
    if (
        doc.custom_minimum_age_limit is not None
        and doc.custom_maximum_age_limit is not None
        and doc.custom_maximum_age_limit < doc.custom_minimum_age_limit
    ):
        frappe.throw(_("Max Age cannot be less than Min Age"))

    # ================= Experience Validation =================
    exp = flt(doc.custom_minimum_experience_no)

    if exp < 0:
        frappe.throw(_("Experience cannot be negative"))