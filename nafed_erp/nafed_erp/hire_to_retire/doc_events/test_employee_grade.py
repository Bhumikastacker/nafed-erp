import frappe
from frappe.tests.utils import FrappeTestCase
from frappe import ValidationError

class TestEmployeeGrade(FrappeTestCase):

    def test_1_positive_grade_creation(self):
        """
        Positive Case: Verify that a valid Employee Grade can be created.
        Focus: Ensuring manual naming (Prompt) and basic currency fields work.
        """
        grade_name = "Management Grade A"
        
        # Cleanup to avoid duplicate error
        if frappe.db.exists("Employee Grade", grade_name):
            frappe.delete_doc("Employee Grade", grade_name)

        grade = frappe.get_doc({
            "doctype": "Employee Grade",
            "name": grade_name,             # Prompt Naming requires 'name'
            "default_base_pay": 50000,
            # Optional Link fields
            "custom_pay_band": None,
            "custom_grade_pay": None,
            # Child Table: custom_basic_pays
            "custom_basic_pays": [
                {
                    "basic_pay": 50000
                }
            ]
        })
        grade.insert()
        
        self.assertTrue(frappe.db.exists("Employee Grade", grade_name))
        print(f"\n[Positive Test] SUCCESS! Created ID: {grade.name}")

    def test_2_numeric_name_gap(self):
        """
        GAP CHECK: Testing if system allows purely numeric names for a Grade.
        """
        numeric_name = "8888"
        if frappe.db.exists("Employee Grade", numeric_name):
            frappe.delete_doc("Employee Grade", numeric_name)

        grade = frappe.get_doc({
            "doctype": "Employee Grade",
            "name": numeric_name
        })

        try:
            grade.insert()
            print("\n[GAP FOUND] Employee Grade allowed PURELY NUMERIC name!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked numeric grade name.")

    def test_3_negative_pay_gap(self):
        """
        GAP CHECK: Testing if system allows negative values in Default Base Pay.
        """
        grade_name = "Negative Pay Test"
        if frappe.db.exists("Employee Grade", grade_name):
            frappe.delete_doc("Employee Grade", grade_name)

        grade = frappe.get_doc({
            "doctype": "Employee Grade",
            "name": grade_name,
            "default_base_pay": -1000 # INVALID DATA
        })

        try:
            grade.insert()
            print("[GAP FOUND] Employee Grade allowed NEGATIVE Default Base Pay!")
        except ValidationError:
            print("[SUCCESS] System blocked negative salary value.")

    def tearDown(self):
        frappe.db.rollback()