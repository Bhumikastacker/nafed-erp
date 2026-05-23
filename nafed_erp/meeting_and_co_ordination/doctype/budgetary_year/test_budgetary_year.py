# Copyright (c) 2026, CSM Technologies Pvt Ltd and Contributors
# See license.txt

# import frappe
# from frappe.tests.utils import FrappeTestCase


# class Testbudgetaryyear(FrappeTestCase):
# 	pass
# ================================================================================================================
import frappe
from frappe.tests.utils import FrappeTestCase
from frappe import ValidationError

class TestBudgetaryYear(FrappeTestCase):

    # ---------------------------------------------------------
    # 1. Positive Test Case
    # ---------------------------------------------------------
    def test_1_positive_year_creation(self):
        """
        CASE 1: Successful creation of a Budgetary Year.
        """
        test_year = "2026-2027"
        
        # Cleanup if exists
        if frappe.db.exists("budgetary year", test_year):
            frappe.db.delete("budgetary year", test_year)

        b_year = frappe.get_doc({
            "doctype": "budgetary year",
            "year": test_year,
            "description": "Standard financial year for testing."
        })
        b_year.insert()
        
        self.assertTrue(frappe.db.exists("budgetary year", b_year.name))
        print(f"\n[Positive Test] SUCCESS! Created Budgetary Year: {b_year.year}")

    # ---------------------------------------------------------
    # 2. Negative Test Case: Mandatory Year Gap
    # ---------------------------------------------------------
    def test_2_missing_year_field_gap(self):
        """
        GAP CHECK: Can we save a record without entering the Year?
        As per JSON, year is reqd: 1.
        """
        b_year = frappe.get_doc({
            "doctype": "budgetary year",
            "description": "Missing year test"
            # year is missing
        })

        try:
            b_year.insert()
            print("\n[GAP FOUND] System allowed Budgetary Year WITHOUT the Year field!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked record without Year.")

    # ---------------------------------------------------------
    # 3. Negative Test Case: Duplicate Year Gap
    # ---------------------------------------------------------
    def test_3_duplicate_year_gap(self):
        """
        GAP CHECK: Can two records have the exact same Year?
        """
        year_val = "2025-2026"
        data = {
            "doctype": "budgetary year",
            "year": year_val
        }
        
        # Create first
        if not frappe.db.exists("budgetary year", year_val):
            frappe.get_doc(data).insert()

        # Try to create second with same Year
        duplicate = frappe.get_doc(data)

        try:
            duplicate.insert()
            # If saved, it's a gap in master data integrity
            print(f"\n[GAP FOUND] System allowed DUPLICATE Budgetary Year: {year_val}")
        except Exception:
            print("\n[SUCCESS] System blocked duplicate Budgetary Year.")

    # ---------------------------------------------------------
    # 4. Behavioral Test Case: Invalid Format Gap
    # ---------------------------------------------------------
    def test_4_invalid_year_format_gap(self):
        """
        GAP CHECK: Does the system allow non-year strings like 'ABCD'?
        """
        b_year = frappe.get_doc({
            "doctype": "budgetary year",
            "year": "ABCD", # INVALID: Not a year format
        })

        try:
            b_year.insert()
            # If saved, there is no format validation
            print(f"\n[GAP FOUND] System allowed non-numeric/invalid year format: {b_year.year}")
        except ValidationError:
            print("\n[SUCCESS] System blocked invalid year format.")

    def tearDown(self):
        frappe.db.rollback()