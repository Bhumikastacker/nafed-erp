# Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document



class LegalAdvocates(Document):
    def validate(self): 
            if self.phone: 
                    if not self.phone.isdigit() or len(self.phone) != 10: 
                            frappe.throw("Phone number is not valid.")

    def after_insert(self):
        self.create_supplier()

    def on_update(self):
        self.create_supplier()

    def create_supplier(self):

        # checkbox check
        if not self.is_supplier:
            return

        advocate_id = self.name
        advocate_name = self.name1

        if not advocate_id or not advocate_name:
            return

        # check if supplier already exists
        supplier = frappe.db.get_value(
            "Supplier",
            {"custom_advocate_name": advocate_id},
            "name"
        )

        if supplier:
            return

        # create supplier
        supplier_doc = frappe.get_doc({
            "doctype": "Supplier",
            "supplier_name": advocate_name,
            "supplier_type": "Individual",
            "supplier_group": "Advocate",
            "custom_advocate_name": advocate_id,
            "custom_other": 1
        })

        supplier_doc.insert(ignore_permissions=True)

        frappe.msgprint("Supplier Created Successfully")