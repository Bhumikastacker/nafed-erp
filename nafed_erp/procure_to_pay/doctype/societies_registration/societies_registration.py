# Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class SocietiesRegistration(Document):

    def on_submit(self):
        self.create_supplier()

    def create_supplier(self):

        # Check if supplier already exists
        if frappe.db.exists("Supplier", {"supplier_name": self.society_name}):
            frappe.msgprint("Supplier already exists")
            return

        supplier = frappe.new_doc("Supplier")

        # -------------------------
        # Basic fields
        # -------------------------
        supplier.naming_series = "SUP-.YYYY.-"
        supplier.supplier_name = self.society_name
        supplier.supplier_group = "All Supplier Groups"
        supplier.supplier_type = "Company"
        supplier.country = self.state and "India" or "India"

        # -------------------------
        # Vendor / Society details
        # -------------------------
        supplier.custom_vendor_code = self.registration_number
        supplier.custom_vendor_category = self.society_type
        supplier.custom_registered_by_society = self.name

        # optional mappings if exist in your doctype
        supplier.custom_contact_person_name = self.contact_person_name
        supplier.custom_mobile_number = self.contact_number
        supplier.custom_email_id = self.email
        supplier.custom_address = self.address
        supplier.custom_district = self.district
        supplier.state = self.state

        # checkbox flags
        supplier.custom_is_sla = 1

        # -------------------------
        # Mandatory Documents Mapping
        # -------------------------
        supplier.custom_pan_card = self.pan
        supplier.custom_gst_certificate = self.gst_certificate

        # -------------------------
        # GST / PAN if available
        # -------------------------
        supplier.gst_category = self.gst_category if hasattr(self, "gst_category") else "Unregistered"
        supplier.tax_id = self.pan_number if hasattr(self, "pan_number") else ""

        # -------------------------
        # Insert supplier
        # -------------------------
        supplier.insert(ignore_permissions=True)

        frappe.msgprint(f"Supplier {supplier.name} created successfully")