# Copyright (c) 2026, CSM Technologies Pvt Ltd and Contributors
# See license.txt

# import frappe
# from frappe.tests.utils import FrappeTestCase


# class TestInternalLegalQuery(FrappeTestCase):
# 	pass

# =======================================================================================================

import frappe
# from frappe.tests.utils import FrappeTestCase


# class TestInternalLegalQuery(FrappeTestCase):
# 	pass

# =======================================================================================================

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe import ValidationError
from frappe.utils import today, add_days
from frappe import ValidationError
from frappe.utils import today, add_days

class TestInternalLegalQuery(FrappeTestCase):

    def setUp(self):
        """
        Setup dependencies: Department and User (Using existing if available).
        """
        # 1. Set up Department – First check if any department already exists.
        self.dept = frappe.db.get_value("Department", {"department_name": "Legal Department"})
        
        if not self.dept:
            # If it does not exist, then create a new one.
            try:
                d = frappe.get_doc({
                    "doctype": "Department",
                    "department_name": "Legal Department"
                }).insert(ignore_permissions=True)
                self.dept = d.name
            except frappe.DuplicateEntryError:
                self.dept = frappe.db.get_value("Department", {"department_name": "Legal Department"})
        
        # 2. Setup Test User with Unique Email
        unique_id = frappe.generate_hash(length=4)
        self.test_user = f"user_{unique_id}@example.com"
        
        if not frappe.db.exists("User", self.test_user):
            user = frappe.get_doc({
                "doctype": "User",
                "email": self.test_user,
                "first_name": "Test",
                "last_name": "User",
                "send_welcome_email": 0
            })
            user.insert(ignore_permissions=True)
            
        frappe.db.commit()
    # ---------------------------------------------------------
    # 1. Positive Test Case
    # ---------------------------------------------------------
    def test_1_positive_query_creation(self):
        """
        CASE 1: Successful creation of an Internal Legal Query.
        """
        query_doc = frappe.get_doc({
            "doctype": "Internal Legal Query",
            "naming_series": "ILQ-.YY.-",
            "raised_by": self.test_user,
            "department": self.dept,
            "urgency_level": "Medium",
            "response_date": add_days(today(), 5),
            "query": "What is the procedure for contract renewal?",
            "status": "Open"
        })
        query_doc.insert()
        
        self.assertTrue(frappe.db.exists("Internal Legal Query", query_doc.name))
        print(f"\n[Positive Test] SUCCESS! Created Query ID: {query_doc.name}")

    # ---------------------------------------------------------
    # 2. Negative Test Case: Missing Mandatory Fields
    # ---------------------------------------------------------
    def test_2_missing_mandatory_fields_gap(self):
        """
        GAP CHECK: Test if system blocks creation without raised_by or department.
        """
        query_doc = frappe.get_doc({
            "doctype": "Internal Legal Query",
            "naming_series": "ILQ-.YY.-",
            "query": "Testing mandatory fields"
            # Missing raised_by, department, and response_date
        })

        try:
            query_doc.insert()
            print("\n[GAP FOUND] System allowed Query without Raised By or Department!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked query due to missing mandatory fields.")

    # ---------------------------------------------------------
    # 3. Negative Test Case: Past Response Date
    # ---------------------------------------------------------
    def test_3_past_response_date_gap(self):
        """
        GAP CHECK: Can we set a requested Response Date in the past?
        """
        past_date = add_days(today(), -10)
        query_doc = frappe.get_doc({
            "doctype": "Internal Legal Query",
            "raised_by": self.test_user,
            "department": self.dept,
            "response_date": past_date, # INVALID: Past Date
            "query": "I need a response 10 days ago."
        })

        try:
            query_doc.insert()
            # If saved, it's a logical gap.
            print(f"\n[GAP FOUND] System allowed a past Response Date ({past_date})!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked past response date.")

    # ---------------------------------------------------------
    # 4. Behavioral Test Case: Empty Query Content
    # ---------------------------------------------------------
    def test_4_empty_query_string_gap(self):
        """
        GAP CHECK: Can we save a query with empty text or just spaces?
        """
        query_doc = frappe.get_doc({
            "doctype": "Internal Legal Query",
            "raised_by": self.test_user,
            "department": self.dept,
            "response_date": add_days(today(), 1),
            "query": "   " # INVALID: Only spaces
        })

        try:
            query_doc.insert()
            print("\n[GAP FOUND] System allowed an empty Query string!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked empty query text.")

    def tearDown(self):
        frappe.db.rollback()
