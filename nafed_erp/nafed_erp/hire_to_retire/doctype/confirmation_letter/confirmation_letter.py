# Copyright (c) 2025, Aarti Kumari and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json
from frappe.utils.pdf import get_pdf
from frappe.utils import getdate, today
class ConfirmationLetter(Document):
    def on_submit(doc):
        if not doc.minimum_pay_scale or not doc.maximum_pay_scale:
            frappe.throw("Kindly update Minimum Pay Scale and Maximum Pay Scale before saving.")



@frappe.whitelist()
def bulk_print(docnames):
    """
    Generate a single PDF using the 'Confirmation Letter Bulk' print format.
    """
    try:
        names = json.loads(docnames)
        if not names:
            frappe.throw("No documents provided for bulk print")

        # Load docs
        docs = [frappe.get_doc("Confirmation Letter", name) for name in names]

        # Load the Print Format doc (must exist)
        pf = frappe.get_doc("Print Format", "Confirmation Letter Bulk")

        # Build rendering context:
        # - docs: full list (what your bulk template expects)
        # - doc: first doc (for any leftover single-doc references)
        # - letter_head / no_letterhead if needed by template
        context = {
            "docs": docs,
            "doc": docs[0],
            "letter_head": frappe.db.get_value("Letter Head", docs[0].get("letter_head") or "", "content") or "",
            "no_letterhead": 0,
            "_context": frappe._dict(),  # keep compatible with some templates
            "frappe": frappe
        }

        # Render the Print Format's HTML with the context
        rendered_html = frappe.render_template(pf.html or pf.html or "", context)

        # Wrap with print styles if your print format doesn't include them.
        # (Optional) You can include frappe's standard print.css via link tags if needed.

        # Convert to PDF
        pdf_data = get_pdf(rendered_html)

        # Return as download response (exactly like ERPNext print->PDF)
        frappe.local.response.filename = "Confirmation_Letters_Bulk.pdf"
        frappe.local.response.filecontent = pdf_data
        frappe.local.response.type = "download"

    except Exception as e:
        frappe.log_error(f"Bulk Print PDF Error: {e}", "Confirmation Letter Bulk Print")
        frappe.throw(str(e))

def create_daily_confirmation_letters():
    current_date = today()

    # Fetch employees whose PPEDate = today
    employees = frappe.db.sql("""
        SELECT 
            name,
            employee_name,
            salutation,
            custom_designation_code,
            custom_place_of_join,
            custom_ppedate
        FROM `tabEmployee`
        WHERE custom_ppedate = %s
    """, (current_date,), as_dict=True)

    if not employees:
        frappe.log_error("No employees found", "Confirmation Scheduler")
        return

    for emp in employees:

        # Check if Confirmation Letter already exists
        status = frappe.db.get_value(
            "Confirmation Letter",
            {"employee_id": emp["name"]},
            "docstatus"
        )

        # If docstatus = 0 (Draft) or 1 (Submitted), skip creation
        if status in [0, 1]:
            continue

        # If docstatus is None or 2 (Cancelled), create new document
        try:
            doc = frappe.new_doc("Confirmation Letter")
            doc.employee_id = emp["name"]
            doc.employee_name = emp["employee_name"]
            doc.salutation = emp["salutation"]
            doc.designation = emp["custom_designation_code"]
            doc.place_of_join = emp["custom_place_of_join"]
            doc.confirmation_date = emp["custom_ppedate"]

            doc.insert(ignore_permissions=True)
        except Exception as e:
            frappe.log_error(frappe.get_traceback(), f"Confirmation Letter Error for {emp['name']}")