# Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
import re
from frappe.model.document import Document


class AuditorEmpanelment(Document):
  import re
import frappe
from frappe.model.document import Document


class AuditorEmpanelment(Document):

    def validate(self):

        # ================= REGISTRATION NO VALIDATION =================
        if self.registration_no:
            registration_no = str(self.registration_no).strip()

            if not registration_no.isdigit():
                frappe.throw("Registration No must contain only numbers.")

            if len(registration_no) != 15:
                frappe.throw("Registration No must be exactly 15 digits.")

        # ================= PAN NO VALIDATION =================
        if self.pan_no:
            pan_no = str(self.pan_no).strip().upper()

            # PAN Format Example: ABCDE1234F
            pan_pattern = r"^[A-Z]{5}[0-9]{4}[A-Z]{1}$"

            if not re.match(pan_pattern, pan_no):
                frappe.throw(
                    "Invalid PAN No format."
                )

            self.pan_no = pan_no

        # ================= EMPANELMENT DATE VALIDATION =================
        if self.empanelment_date and self.expiry_date:

            if self.expiry_date <= self.empanelment_date:
                frappe.throw(
                    "Empanelment End Date cannot be earlier than Empanelment Start Date."
                )

@frappe.whitelist()
def update_auditor_empanelment(purchase_invoice, supplier):

    supplier_doc = frappe.get_doc("Supplier", supplier)

    # Supplier group check
    if supplier_doc.supplier_group != "Statutory":
        return

    # Auditor Empanelment link check
    if not supplier_doc.custom_auditor_empanelment:
        return

    auditor = frappe.get_doc(
        "Auditor Empanelment",
        supplier_doc.custom_auditor_empanelment
    )

    # Only update if not already mapped
    if not auditor.purchase_invoice:
        auditor.purchase_invoice = purchase_invoice
        auditor.save(ignore_permissions=True)