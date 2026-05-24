# Copyright (c) 2026, CSM Technologies Pvt Ltd and Contributors
# See license.txt

# import frappe
# from frappe.tests.utils import FrappeTestCase


# class TestInvestigation(FrappeTestCase):
# 	pass

# =====================================================================================================

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe import ValidationError
from frappe.utils import today

class TestInvestigation(FrappeTestCase):

    def setUp(self):
        """
        Setup dependency: Complaint Receipt.
        """
        # Create a dummy Complaint Receipt
        self.receipt = frappe.get_doc({
            "doctype": "Complaint Receipts",
            "complaint_type": "Anonymous",
            "date": today()
        }).insert(ignore_permissions=True)
        
        frappe.db.commit()

    # ---------------------------------------------------------
    # 1. Positive Test Case
    # ---------------------------------------------------------
    def test_1_positive_investigation_creation(self):
        """
        CASE 1: Successful creation of an Investigation linked to a Receipt.
        """
        inv = frappe.get_doc({
            "doctype": "Investigation",
            "naming_series": "IN-.YYYY.-.####",
            "complaint_receipt": self.receipt.name,
            "remarks": "Investigation started based on anonymous complaint."
        })
        inv.insert()
        
        self.assertTrue(frappe.db.exists("Investigation", inv.name))
        print(f"\n[Positive Test] SUCCESS! Created Investigation ID: {inv.name}")

    # ---------------------------------------------------------
    # 2. Negative Test Case: Orphan Investigation Gap
    # ---------------------------------------------------------
    def test_2_orphan_investigation_gap(self):
        """
        GAP CHECK: Can we save an investigation without linking a Complaint Receipt?
        As per JSON, reqd is 0, which is a potential process gap.
        """
        inv = frappe.get_doc({
            "doctype": "Investigation",
            "remarks": "Ghost Investigation without any receipt link"
            # Missing complaint_receipt
        })

        try:
            inv.insert()
            # If it saves, it's a gap. An investigation must always belong to a complaint.
            print("\n[GAP FOUND] System allowed Investigation WITHOUT a Complaint Receipt link!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked investigation without receipt.")

    # ---------------------------------------------------------
    # 3. Negative Test Case: Duplicate Investigation Gap
    # ---------------------------------------------------------
    def test_3_duplicate_investigation_gap(self):
        """
        GAP CHECK: Can we start two investigations for the same complaint?
        """
        data = {
            "doctype": "Investigation",
            "complaint_receipt": self.receipt.name,
            "remarks": "First investigation"
        }
        frappe.get_doc(data).insert()

        # Try to create second for same receipt
        duplicate = frappe.get_doc({
            "doctype": "Investigation",
            "complaint_receipt": self.receipt.name,
            "remarks": "Duplicate investigation attempt"
        })

        try:
            duplicate.insert()
            print("\n[GAP FOUND] System allowed DUPLICATE Investigations for the same Complaint Receipt!")
        except Exception:
            print("\n[SUCCESS] System blocked duplicate investigation.")

    # ---------------------------------------------------------
    # 4. Behavioral Test Case: Empty Investigation
    # ---------------------------------------------------------
    def test_4_empty_investigation_gap(self):
        """
        GAP CHECK: Can we save an investigation without members or remarks?
        """
        inv = frappe.get_doc({
            "doctype": "Investigation",
            "complaint_receipt": self.receipt.name,
            "members": [],
            "remarks": ""
        })

        try:
            inv.insert()
            print("\n[GAP FOUND] System allowed an EMPTY Investigation record!")
        except ValidationError:
            print("\n[SUCCESS] System blocked investigation without details.")

    def tearDown(self):
        frappe.db.rollback()