# Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _


class InvestmentSocieties(Document):
	def before_insert(self):
		self.create_supplier_for_society()


	def create_supplier_for_society(doc, method=None):

		# 1️⃣ Get Supplier Group marked as Society
		supplier_group = frappe.db.get_value(
			"Supplier Group",
			{"custom_is_society": 1},
			"name"
		)

		if not supplier_group:
			frappe.throw(_("Please enable 'Is Society' in one Supplier Group first."))

		# 2️⃣ Prevent duplicate supplier
		existing_supplier = frappe.db.exists(
			"Supplier",
			{"supplier_name": doc.society_name or doc.society_code}
		)

		if existing_supplier:
			return

		# 3️⃣ Create Supplier
		supplier = frappe.new_doc("Supplier")
		supplier.supplier_name = doc.society_name or doc.society_code
		supplier.supplier_group = supplier_group
		supplier.supplier_type = "Company"

		supplier.gstin = doc.gstin
		supplier.pan = doc.pan_id
		supplier.custom_tan_id = doc.tan_id
		supplier.email_id = doc.email_id
		supplier.mobile_no = doc.phone_no

		if doc.address:
			supplier.supplier_primary_address=doc.address
		supplier.insert(ignore_permissions=True)
