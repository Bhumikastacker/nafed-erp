# Copyright (c) 2025, CSM Technologies Pvt Ltd and Contributors
# See license.txt

# # import frappe
# from frappe.tests.utils import FrappeTestCase


# class TestChildrenAllowanceDeclaration(FrappeTestCase):
# 	pass


import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import today, add_days
from frappe import ValidationError

class TestChildrenAllowanceDeclaration(FrappeTestCase):

    def setUp(self):
        """
        Set up pre-requisites: Employee and Salary Component.
        """
        self.company = "_Test Indian Registered Company"
        
        # 1. Ensure 'Children Education Allowance' Salary Component exists
        if not frappe.db.exists("Salary Component", "Children Education Allowance"):
            frappe.get_doc({
                "doctype": "Salary Component",
                "salary_component": "Children Education Allowance",
                "type": "Earning"
            }).insert()

        # 2. Create a dummy Employee
        if not frappe.db.exists("Employee", {"first_name": "AllowanceUser"}):
            emp = frappe.get_doc({
                "doctype": "Employee",
                "employee_number": "EMP-CAD-101",
                "first_name": "AllowanceUser",
                "gender": "Male",
                "date_of_joining": "2020-01-01",
                "status": "Active",
                "company": self.company,
                "date_of_birth": "1990-01-01",
                "pan_number": "ABCDE1234F",
                "custom_uan_number": "111122223333",
                "custom_vpf_applicable": "No",
                "custom_ppedate": "2020-01-01",
                "custom_allotted_official_accommodation": "No"
            })
            emp.insert()
            self.test_employee = emp.name
        else:
            self.test_employee = frappe.db.get_value("Employee", {"first_name": "AllowanceUser"}, "name")

        frappe.db.commit()

    # ------------------------
    # Positive Test Case
    # ------------------------
    def test_1_positive_declaration_creation(self):
        """
        CASE 1: Verify successful creation of a valid Children Allowance Declaration.
        """
        declaration = frappe.get_doc({
            "doctype": "Children Allowance Declaration",
            "employee": self.test_employee,
            "date_of_application": today(),
            "order_no": "ORD-2026-001",
            "salary_component": "Children Education Allowance",
            "amount": 2000,
            # --- MANDATORY CHILD TABLE ---
            "children_details": [
                {
                    "child_name": "Baby Doe",
                    "date_of_birth": "2015-05-10"
                }
            ]
        })
        declaration.insert()
        self.assertTrue(frappe.db.exists("Children Allowance Declaration", declaration.name))
        print(f"\n[Positive Test] SUCCESS! Created ID: {declaration.name}")

    # ------------------------
    # Negative Test Case
    # ------------------------
    def test_2_negative_amount_gap(self):
        """
        GAP CHECK: Testing if system allows a NEGATIVE allowance amount.
        """
        declaration = frappe.get_doc({
            "doctype": "Children Allowance Declaration",
            "employee": self.test_employee,
            "date_of_application": today(),
            "order_no": "ORD-NEG-001",
            "salary_component": "Children Education Allowance",
            "amount": -500, # INVALID DATA
            "children_details": [{"child_name": "Test Child"}]
        })

        try:
            declaration.insert()
            print("\n[GAP FOUND] System allowed NEGATIVE Allowance Amount!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked negative amount.")

    # ------------------------
    # Negative Test Case
    # ------------------------
    def test_3_empty_child_table_gap(self):
        """
        GAP CHECK: Testing if system allows saving without any Children Details.
        """
        declaration = frappe.get_doc({
            "doctype": "Children Allowance Declaration",
            "employee": self.test_employee,
            "date_of_application": today(),
            "order_no": "ORD-EMPTY-01",
            "salary_component": "Children Education Allowance",
            "amount": 1000,
            "children_details": [] # INVALID: Empty Table
        })

        try:
            declaration.insert()
            print("[GAP FOUND] System allowed declaration WITHOUT any Children Details!")
        except ValidationError:
            print("[SUCCESS] System correctly blocked empty child table.")

    def tearDown(self):
        frappe.db.rollback()
