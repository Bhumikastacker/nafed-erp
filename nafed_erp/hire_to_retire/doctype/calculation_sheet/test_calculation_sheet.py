# Copyright (c) 2026, CSM Technologies Pvt Ltd and Contributors
# See license.txt

# import frappe
# from frappe.tests.utils import FrappeTestCase


# class TestCalculationSheet(FrappeTestCase):
# 	pass

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import getdate

class TestCalculationSheet(FrappeTestCase):
    def setUp(self):
        # Dummy Salary Component
        if not frappe.db.exists("Salary Component", "Test Allowance"):
            frappe.get_doc({
                "doctype": "Salary Component",
                "salary_component": "Test Allowance",
                "type": "Earning",
                "custom_default_percentage_": 10
            }).insert()

        # Dummy Employee
        if not frappe.db.exists("Employee", {"first_name": "Test User"}):
            emp = frappe.get_doc({
                "doctype": "Employee",
                "employee_number": "EMP-T-001",
                "naming_series": "EMP-",
                "first_name": "Test User",
                "gender": "Male",
                "date_of_joining": "2020-01-01",
                "status": "Active",
                "custom_basic_pay": 50000,
                "date_of_birth": "1990-01-01",
                "pan_number": "ABCDE1234F",
                "custom_allotted_official_accommodation": "No",
                "custom_uan_number": "123456789012",
                "custom_vpf_applicable": 0,
                "custom_ppedate": "2020-01-01"
            })
            emp.insert()
            self.test_emp = emp.name
        else:
            self.test_emp = frappe.db.get_value("Employee", {"first_name": "Test User"}, "name")

    def test_arrears_calculation_logic(self):
        doc = frappe.get_doc({
            "doctype": "Calculation Sheet",
            "type": "Arrears",
            "salary_component": "Test Allowance",
            "current_compensation_": 10,
            "revised_compensation_": 20,
            "company": "Stackerbee Technologies"
        })
        arrears = doc.calculate_dynamic_arrears()
        self.assertTrue(len(arrears) > 0)

    def test_create_additional_salaries(self):
        doc = frappe.get_doc({
            "doctype": "Calculation Sheet",
            "type": "Arrears",
            "salary_component": "Test Allowance",
            "current_compensation_": 10,
            "revised_compensation_": 20,
            "payroll_entry_date": getdate(),
            "company": "Stackerbee Technologies",
            "component_details": [
                {
                    "employee": self.test_emp,
                    "final_amount": 5000
                }
            ]
        })
        doc.insert()
        doc.submit()
        count = doc.create_additional_salaries()
        self.assertIsInstance(count, int)

    def tearDown(self):
        pass