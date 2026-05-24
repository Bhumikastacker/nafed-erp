# Copyright (c) 2026, CSM Technologies Pvt Ltd and Contributors
# See license.txt

# import frappe
# from frappe.tests.utils import FrappeTestCase


# class TestJurisdiction(FrappeTestCase):
# 	pass

# =======================================================================================================

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe import ValidationError

class TestJurisdiction(FrappeTestCase):

    # ------------------------
    # Positive Test Case
    # ------------------------
    def test_1_positive_jurisdiction_creation(self):
        """
        CASE 1: Verify successful creation of a Jurisdiction.
        """
        jur_name = "Supreme Court of India"
        
        # Cleanup existing to avoid unique constraint error
        if frappe.db.exists("Jurisdiction", jur_name):
            frappe.delete_doc("Jurisdiction", jur_name)

        jurisdiction = frappe.get_doc({
            "doctype": "Jurisdiction",
            "name1": jur_name, # Mandatory and Unique field
            "address": "Tilak Marg, New Delhi, Delhi 110001"
        })
        jurisdiction.insert()
        
        # Assertion: Check if record exists
        self.assertTrue(frappe.db.exists("Jurisdiction", jur_name))
        print(f"\n[Positive Test] SUCCESS! Created Jurisdiction: {jurisdiction.name1}")

    # ------------------------
    # Negative Test Case (Gap Check)
    # ------------------------
    def test_2_missing_mandatory_name_gap(self):
        """
        GAP CHECK: Testing if system allows creation without Name (name1 is reqd: 1).
        """
        jurisdiction = frappe.get_doc({
            "doctype": "Jurisdiction",
            "address": "Some Address"
            # name1 is missing
        })

        try:
            jurisdiction.insert()
            print("\n[GAP FOUND] Jurisdiction allowed creation WITHOUT mandatory Name (name1)!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked Jurisdiction without Name.")

    # ------------------------
    # Negative Test Case (Gap Check)
    # ------------------------
    def test_3_duplicate_name_gap(self):
        """
        GAP CHECK: Testing if system allows duplicate names (unique: 1).
        """
        jur_name = "High Court Delhi"
        
        # Create first record
        if not frappe.db.exists("Jurisdiction", jur_name):
            frappe.get_doc({
                "doctype": "Jurisdiction",
                "name1": jur_name
            }).insert()

        # Try to create duplicate
        duplicate_jur = frappe.get_doc({
            "doctype": "Jurisdiction",
            "name1": jur_name
        })

        try:
            duplicate_jur.insert()
            print(f"\n[GAP FOUND] System allowed DUPLICATE Jurisdiction Name: {jur_name}")
        except (ValidationError, frappe.UniqueValidationError, Exception):
            print("\n[SUCCESS] System correctly blocked duplicate Jurisdiction name.")

    def tearDown(self):
        """
        Rollback changes.
        """
        frappe.db.rollback()
