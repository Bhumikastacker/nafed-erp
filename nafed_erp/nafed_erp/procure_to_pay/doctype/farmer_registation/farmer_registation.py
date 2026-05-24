# Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
# For license information, please see license.txt
import re
import frappe
from frappe.model.document import Document

from frappe.utils import today, getdate

class FarmerRegistation(Document):
	def on_submit(self):
		self.create_supplier_from_farmer()

	def create_supplier_from_farmer(self):
			# check if supplier already exists with same farmer_id or mobile/email (recommended)
			existing_supplier = frappe.db.get_value(
				"Supplier",
				{"mobile_no": self.mobile_no},
				"name"
			)

			if existing_supplier:
				frappe.msgprint(f"Supplier already exists: {existing_supplier}")
				return

			# create supplier
			supplier = frappe.new_doc("Supplier")

			supplier.supplier_name = self.farmer_name
			supplier.supplier_type = "Individual"

			# custom fields mapping
			supplier.mobile_no = self.mobile_no
			supplier.email_id = self.email_id
			supplier.custom_society = self.society

			# ✅ tick "Is Farmer" checkbox
			supplier.custom_is_farmer = 1

			supplier.insert(ignore_permissions=True)

			# link supplier back to farmer registration
			self.db_set("registered_by_society", supplier.name)

			frappe.msgprint(f"Supplier created successfully: {supplier.name}")


			from frappe.utils import today, getdate

	def validate(self):
		if self.date_of_birth:
			dob = getdate(self.date_of_birth)
			today_date = getdate(today())

			age = today_date.year - dob.year - ((today_date.month, today_date.day) < (dob.month, dob.day))

			self.age = age
		
		# ==========================
		# 1. Aadhaar Length Check
		# ==========================
		if self.aadhaar_no and len(str(self.aadhaar_no)) != 12:
			frappe.throw("Aadhaar Number must be exactly 12 digits.")

		# ===========================
		# 2. Duplicate Aadhaar Check
		# ===========================
		if self.aadhaar_no:
			duplicate = frappe.db.exists("Farmer Registation", {"aadhaar_no": self.aadhaar_no, "name": ["!=", self.name]})
			if duplicate:
				frappe.throw(f"Aadhaar {self.aadhaar_no} is already registered!")

		# ========================
		# 3. Mobile Length Check
		# ========================
		if self.mobile_no and len(str(self.mobile_no)) != 10:
			frappe.throw("Mobile number must be exactly 10 digits.")

		# ==============================
		# Duplicate Mobile Number Check
		# ==============================
		if self.mobile_no:
			dup_mobile = frappe.db.exists("Farmer Registation", {
				"mobile_no": self.mobile_no, 
				"name": ["!=", self.name] 
			})
			if dup_mobile:
				frappe.throw(f"Mobile number {self.mobile_no} is already registered with another farmer!")

		# =======================
		# 4. Email Format Check 
		# =======================
		if self.email_id:
			pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$" # regex 
			if not re.match(pattern, self.email_id) or ".. " in self.email_id or "@-" in self.email_id:
				frappe.throw("The Email ID you entered is invalid. Please check the format.")