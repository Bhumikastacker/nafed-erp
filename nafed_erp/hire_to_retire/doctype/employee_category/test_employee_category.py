# # Copyright (c) 2025, sam  and Contributors
# # See license.txt


import frappe
from frappe.tests.utils import FrappeTestCase
from frappe import ValidationError

class TestEmployeeCategory(FrappeTestCase):

    def test_1_positive_category_creation(self):
        """
        Positive Case: Create a standard Employee Category.
        """
        cat_name = "Permanent Test"
        if frappe.db.exists("Employee Category", cat_name):
            frappe.delete_doc("Employee Category", cat_name)

        category = frappe.get_doc({
            "doctype": "Employee Category",
            "employee_category_name": cat_name,
            "emp_cat_code": "CAT-01"
        })
		
        category.insert()
        self.assertTrue(frappe.db.exists("Employee Category", cat_name))
        print(f"\n[Positive Test] SUCCESS! Created ID: {category.name}")

    def test_2_duplicate_name_gap(self):
        """
        GAP CHECK: Testing if duplicate names are correctly blocked.
        """
        cat_name = "Duplicate Category"
        if not frappe.db.exists("Employee Category", cat_name):
            frappe.get_doc({"doctype": "Employee Category", "employee_category_name": cat_name}).insert()

        # Attempt to create duplicate
        duplicate = frappe.get_doc({
            "doctype": "Employee Category",
            "employee_category_name": cat_name
        })

        try:
            duplicate.insert()
            print("\n[GAP FOUND] System allowed DUPLICATE Employee Categories!")
        except frappe.DuplicateEntryError:
            print("\n[SUCCESS] System correctly blocked duplicate category name.")

    def test_3_numeric_name_gap(self):
        """
        GAP CHECK: Testing if purely numeric names are allowed for master data.
        """
        numeric_name = "9999"
        if frappe.db.exists("Employee Category", numeric_name):
            frappe.delete_doc("Employee Category", numeric_name)

        category = frappe.get_doc({
            "doctype": "Employee Category",
            "employee_category_name": numeric_name
        })

        try:
            category.insert()
            print("[GAP FOUND] Employee Category allowed PURELY NUMERIC name!")
        except ValidationError:
            print("[SUCCESS] System blocked numeric master data name.")

    def tearDown(self):
        frappe.db.rollback()