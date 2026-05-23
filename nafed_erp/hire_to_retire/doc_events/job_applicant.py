import frappe
import re
from frappe import _
from frappe.utils import validate_email_address

def validate(doc, method):

    # ===================
    # 1. Phone Validation 
    # ===================
    if doc.phone_number:
        pattern = r'^[6-9]\d{9}$'
        if not re.match(pattern, doc.phone_number):
            frappe.throw(_("Enter valid mobile number (10 digits starting with 6-9)"))
    
    # ==============================
	# Duplicate Phone Number Check
	# ==============================
    if doc.phone_number:
        existing = frappe.db.exists(
            "Job Applicant",
            {
                "phone_number": doc.phone_number,
                "name": ["!=", doc.name]
            }
        )

        if existing:
            frappe.throw(
                _("Mobile number {0} is already registered with another applicant").format(doc.phone_number)
            )

    # =======================
	# 4. Email Format Check 
	# =======================
    if doc.email_id:
        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$" # regex 
        if not re.match(pattern, doc.email_id) or ".. " in doc.email_id or "@-" in doc.email_id:
            frappe.throw("The Email ID you entered is invalid. Please check the format.")

    # ===============================
    # 3. Duplicate Email Check
    # ===============================
    if doc.email_id:
        existing = frappe.db.exists(
            "Job Applicant",
            {
                "email_id": doc.email_id,
                "name": ["!=", doc.name]
            }
        )

        if existing:
            frappe.throw(_("An applicant with this email already exists"))