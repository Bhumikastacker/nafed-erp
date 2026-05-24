# Copyright (c) 2025, CSM Technologies Pvt Ltd and Contributors
# See license.txt

# import frappe
# from frappe.tests.utils import FrappeTestCase


# class TestImmovablePropertyManagement(FrappeTestCase):
# 	pass


import frappe
from frappe.tests.utils import FrappeTestCase
from frappe import ValidationError

class TestImmovablePropertyManagement(FrappeTestCase):

    def setUp(self):
        """
        Set up pre-requisites for property management.
        """
        self.company = "_Test Indian Registered Company"
        
        # Create a dummy Employee
        if not frappe.db.exists("Employee", {"first_name": "PropertyUser"}):
            emp = frappe.get_doc({
                "doctype": "Employee",
                "employee_number": "EMP-IPM-999",
                "first_name": "PropertyUser",
                "gender": "Male",
                "date_of_joining": "2020-01-01",
                "status": "Active",
                "company": self.company,
                "date_of_birth": "1985-01-01",
                "pan_number": "ABCDE1111Z",
                "custom_uan_number": "111122223333",
                "custom_vpf_applicable": "No",
                "custom_ppedate": "2020-01-01",
                "custom_allotted_official_accommodation": "No"
            }).insert()
            self.test_employee = emp.name
        else:
            self.test_employee = frappe.db.get_value("Employee", {"first_name": "PropertyUser"}, "name")

        frappe.db.commit()

    # ------------------------
    # Positive Test Case
    # ------------------------
    def test_1_positive_property_creation(self):
        """
        CASE 1: Verify successful creation with all mandatory child table fields.
        """
        property_doc = frappe.get_doc({
            "doctype": "Immovable Property Management",
            "employee": self.test_employee,
            "not_applicable": 0,
            "details": [
                {
                    # Updated fields based on your MandatoryError
                    "present_value": 5000000, 
                    "remarks": "Self-owned apartment",
                    "description": "2BHK Flat" # Assuming this field exists
                }
            ]
        })
        property_doc.insert()
        self.assertTrue(frappe.db.exists("Immovable Property Management", property_doc.name))
        print(f"\n[Positive Test] SUCCESS! Created ID: {property_doc.name}")

    # ------------------------
    # Negative Test Case
    # ------------------------
    def test_2_empty_details_gap(self):
        """
        GAP CHECK: Testing if system allows saving when 'Not Applicable' is UNCHECKED 
        but the 'Details' table is empty.
        """
        property_doc = frappe.get_doc({
            "doctype": "Immovable Property Management",
            "employee": self.test_employee,
            "not_applicable": 0, 
            "details": [] # INVALID: Should have rows if not applicable is 0
        })

        try:
            property_doc.insert()
            print("\n[GAP FOUND] System allowed saving record with EMPTY property details!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked empty property table.")

    # ------------------------
    # Negative Test Case
    # ------------------------
    def test_3_not_applicable_with_data_gap(self):
        """
        GAP CHECK: Testing if 'Not Applicable' can be checked while providing table data.
        """
        property_doc = frappe.get_doc({
            "doctype": "Immovable Property Management",
            "employee": self.test_employee,
            "not_applicable": 1, # Conflicting with data below
            "details": [
                {
                    "present_value": 100000,
                    "remarks": "Test Gap"
                }
            ]
        })

        try:
            property_doc.insert()
            print("[GAP FOUND] System allowed 'Not Applicable' to be checked while having data rows!")
        except ValidationError:
            print("[SUCCESS] System blocked contradictory data.")

    def tearDown(self):
        frappe.db.rollback()
