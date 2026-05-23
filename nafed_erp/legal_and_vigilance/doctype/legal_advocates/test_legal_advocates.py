# Copyright (c) 2026, CSM Technologies Pvt Ltd and Contributors
# See license.txt

# import frappe
# from frappe.tests.utils import FrappeTestCase


# class TestLegalAdvocates(FrappeTestCase):
# 	pass

# =========================================================================================================

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe import ValidationError

class TestLegalAdvocates(FrappeTestCase):

    def setUp(self):
        """
        Set up pre-requisites: Ensure a valid Advocate Fee Schedule exists.
        """
        self.fee_schedule_name = "Standard Fee 2026"
        
        # If it doesn't exist, create it with basic mandatory fields
        if not frappe.db.exists("Advocate Fee Schedule", self.fee_schedule_name):
            doc = frappe.get_doc({
                "doctype": "Advocate Fee Schedule",
                "name": self.fee_schedule_name,
                "fee_schedule_name": self.fee_schedule_name,
                # Add other mandatory fields for Fee Schedule if any exist
            })
            doc.insert(ignore_permissions=True)
            frappe.db.commit() # Important for link validation in tests

    # ------------------------
    # 1. Positive Test Case
    # ------------------------
    def test_1_positive_advocate_creation(self):
        """
        CASE 1: Verify successful creation of a Legal Advocate with all mandatory fields.
        """
        adv_name = "Advocate John Doe"
        
        # Cleanup existing to avoid unique constraint error
        if frappe.db.exists("Legal Advocates", adv_name):
            frappe.delete_doc("Legal Advocates", adv_name)

        advocate = frappe.get_doc({
            "doctype": "Legal Advocates",
            "name1": adv_name,
            "phone": "9876543210",
            "mail": "john.doe@legal.com",
            "empanelment_status": "Active",
            "max_active_cases": 10,
            "advocate_fee_schedule": self.fee_schedule_name,
            "address": "Supreme Court Chambers"
        })
        advocate.insert()
        
        # Assertion: Check if record exists
        self.assertTrue(frappe.db.exists("Legal Advocates", adv_name))
        print(f"\n[Positive Test] SUCCESS! Created Advocate: {advocate.name1}")

    # ------------------------
    # 2. Negative Test Case (Mandatory Field Gap)
    # ------------------------
    def test_2_missing_fee_schedule_gap(self):
        """
        GAP CHECK: Testing if system blocks creation without Fee Schedule (reqd: 1).
        """
        advocate = frappe.get_doc({
            "doctype": "Legal Advocates",
            "name1": "No Fee Advocate",
            "phone": "1122334455",
            "mail": "nofee@legal.com",
            "empanelment_status": "Active",
            "max_active_cases": 5
            # advocate_fee_schedule is missing
        })

        try:
            advocate.insert()
            # If saved, it's a GAP (Bug)
            print("\n[GAP FOUND] System allowed Advocate WITHOUT Fee Schedule!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked Advocate without Fee Schedule.")

    # ------------------------
    # 3. Negative Test Case (Invalid Phone Gap)
    # ------------------------
    def test_3_invalid_phone_length_gap(self):
        """
        GAP CHECK: Testing if system allows phone number other than 10 digits.
        As per JSON, the max length is set to 10.
        """
        advocate = frappe.get_doc({
            "doctype": "Legal Advocates",
            "name1": "Short Phone Advocate",
            "phone": "123", # INVALID length
            "mail": "short@legal.com",
            "empanelment_status": "Active",
            "max_active_cases": 5,
            "advocate_fee_schedule": self.fee_schedule_name
        })

        try:
            advocate.insert()
            # Often Frappe only validates length on UI; if saved here, it's a backend GAP.
            print(f"\n[GAP FOUND] Advocate allowed with invalid phone length: {advocate.phone}")
        except (ValidationError, Exception):
            print("\n[SUCCESS] System blocked invalid phone length.")

    # ------------------------
    # 4. Negative Test Case (Unique Field Gap)
    # ------------------------
    def test_4_duplicate_email_gap(self):
        """
        GAP CHECK: Testing if duplicate emails are allowed (unique: 1).
        """
        email = "duplicate@legal.com"
        
        # Create first record
        frappe.get_doc({
            "doctype": "Legal Advocates",
            "name1": "Advocate Alpha",
            "phone": "9000000001",
            "mail": email,
            "empanelment_status": "Active",
            "max_active_cases": 5,
            "advocate_fee_schedule": self.fee_schedule_name
        }).insert()

        # Try to create second record with same email
        duplicate = frappe.get_doc({
            "doctype": "Legal Advocates",
            "name1": "Advocate Beta",
            "phone": "9000000002",
            "mail": email,
            "empanelment_status": "Active",
            "max_active_cases": 5,
            "advocate_fee_schedule": self.fee_schedule_name
        })

        try:
            duplicate.insert()
            print(f"\n[GAP FOUND] System allowed DUPLICATE Email: {email}")
        except (ValidationError, Exception):
            print("\n[SUCCESS] System correctly blocked duplicate email.")

    # ------------------------
    # 5. Negative Test Case (Non-Negative Gap)
    # ------------------------
    def test_5_negative_cases_limit_gap(self):
        """
        GAP CHECK: Testing if Max Active Cases allows negative numbers.
        As per JSON, non_negative: 1.
        """
        advocate = frappe.get_doc({
            "doctype": "Legal Advocates",
            "name1": "Negative Case Advocate",
            "phone": "8000000000",
            "mail": "neg@legal.com",
            "empanelment_status": "Active",
            "max_active_cases": -5, # INVALID negative value
            "advocate_fee_schedule": self.fee_schedule_name
        })

        try:
            advocate.insert()
            print(f"\n[GAP FOUND] System allowed NEGATIVE Max Active Cases: {advocate.max_active_cases}")
        except (ValidationError, Exception):
            print("\n[SUCCESS] System correctly blocked negative case value.")

    def tearDown(self):
        """
        Rollback changes to keep the database clean.
        """
        frappe.db.rollback()