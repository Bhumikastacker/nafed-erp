import frappe
from frappe.tests.utils import FrappeTestCase
from frappe import ValidationError

class TestEmploymentType(FrappeTestCase):

    def test_1_positive_employment_type_creation(self):
        """
        Positive Case: Verify that a valid Employment Type can be created.
        """
        type_name = "Full-time Test"
        
        # Cleanup if exists to ensure a fresh test
        if frappe.db.exists("Employment Type", type_name):
            frappe.delete_doc("Employment Type", type_name)

        emp_type = frappe.get_doc({
            "doctype": "Employment Type",
            "employee_type_name": type_name, # Mandatory field (acts as ID)
            "custom_employment_type_code": "FT-01",
            "custom_payroll_entry_date": 1
        })
        emp_type.insert()
        # frappe.db.commit()
        
        # Assert the record exists in database
        self.assertTrue(frappe.db.exists("Employment Type", type_name))
        print(f"\n[Positive Test] SUCCESS! Created ID: {emp_type.name}")

    def test_2_numeric_name_gap(self):
        """
        GAP CHECK: Testing if system allows purely numeric names for master data.
        """
        numeric_name = "123456" # INVALID DATA
        
        if frappe.db.exists("Employment Type", numeric_name):
            frappe.delete_doc("Employment Type", numeric_name)

        emp_type = frappe.get_doc({
            "doctype": "Employment Type",
            "employee_type_name": numeric_name
        })

        try:
            emp_type.insert()
            print("\n[GAP FOUND] Employment Type allowed PURELY NUMERIC name!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked numeric master data name.")

    def test_3_duplicate_name_gap(self):
        """
        GAP CHECK: Verify that duplicate names are blocked.
        """
        type_name = "Duplicate Test"
        
        # Create first record
        if not frappe.db.exists("Employment Type", type_name):
            frappe.get_doc({
                "doctype": "Employment Type",
                "employee_type_name": type_name
            }).insert()

        # Attempt to create second record with SAME name
        duplicate = frappe.get_doc({
            "doctype": "Employment Type",
            "employee_type_name": type_name
        })

        try:
            duplicate.insert()
            print("[GAP FOUND] System allowed DUPLICATE Employment Type names!")
        except frappe.DuplicateEntryError:
            print("[SUCCESS] System correctly blocked duplicate names.")

    def tearDown(self):
        """
        Rollback changes after the test.
        """
        frappe.db.rollback()
        # pass