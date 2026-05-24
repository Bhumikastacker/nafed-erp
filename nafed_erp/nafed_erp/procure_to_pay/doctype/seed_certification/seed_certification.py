# Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import nowdate, getdate
from frappe.utils.pdf import get_pdf

class SeedCertification(Document):

    def validate(self):
        self.validate_lab_results()
        if (
            self.certification_status == "QA Verified"
            and not self.certification_number
        ):
            self.generate_certification_number()
        

    def before_submit(self):
        self.update_lot_status()
   
    def validate_lab_results(self):
      if self.germination_ and self.germination_ < 85:
        frappe.throw("Germination must be >= 85%")
      if self.purity_ and self.purity_ < 98:
        frappe.throw("Purity must be >= 98%")

    def generate_certification_number(self):
    #   if not self.certification_number:
        year = frappe.utils.nowdate()[:4]
        state_map = {
            "Delhi": "DL",
            "Tamil Nadu": "TN",
            "Maharashtra": "MH",
            "Karnataka": "KA"
        }
        state_code = state_map.get(self.state, "NA")
        crop_name = frappe.db.get_value("Crop", self.crop, "crop_name") or "CROP"
        crop_code = crop_name.upper()
        lot = self.lot_id or "LOT-0000"
        lot_parts = lot.split("-")
        lot_sequence = lot_parts[-1]
        self.certification_number = f"{state_code}-{year}-{crop_code}-LOT-{lot_sequence}"

    # def update_lot_status(self):
    #     if self.lot_id:
    #         lot = frappe.get_doc("Lot", self.lot_id)
    #         lot.status = "Certified"
    #         lot.save(ignore_permissions=True)

    def generate_certificate(self):
        frappe.msgprint("PDF generation triggered")
        html = frappe.get_print(
            "Seed Certification",
            self.name,
            print_format="Seed Certification Certificate"
        )
        pdf = get_pdf(html)

        file_doc = frappe.get_doc({
            "doctype": "File",
            "file_name": f"{self.name}.pdf",
            "attached_to_doctype": "Seed Certification",
            "attached_to_name": self.name,
            "content": pdf
        })
        file_doc.insert(ignore_permissions=True)

    def on_submit(self):
        self.generate_certificate()
        
    def generate_barcode(self):
        if not self.barcode_no:
            self.barcode_no = f"{self.lot_id}-{frappe.utils.nowdate()}"

    def before_save(self):
        self.generate_barcode()
        
