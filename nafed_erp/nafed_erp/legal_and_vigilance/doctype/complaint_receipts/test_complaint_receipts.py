# Copyright (c) 2026, CSM Technologies Pvt Ltd and Contributors
# See license.txt

# import frappe
# from frappe.tests.utils import FrappeTestCase


# class TestComplaintReceipts(FrappeTestCase):
# 	pass

# ========================================================================================================

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe import ValidationError
from frappe.utils import today

class TestComplaintReceipts(FrappeTestCase):

    # ---------------------------------------------------------
    # 1. Positive Test Case
    # ---------------------------------------------------------
    def test_1_positive_anonymous_complaint_creation(self):
        """
        CASE 1: Successful creation of an Anonymous Complaint.
        """
        receipt = frappe.get_doc({
            "doctype": "Complaint Receipts",
            "naming_series": "VIG/.YYYY./.###.",
            "complaint_type": "Anonymous",
            "date": today(),
            "complainant_name": "" 
        })
        receipt.insert()
        
        self.assertTrue(frappe.db.exists("Complaint Receipts", receipt.name))
        print(f"\n[Positive Test] SUCCESS! Created Anonymous Complaint ID: {receipt.name}")

    # ---------------------------------------------------------
    # 2. Negative Test Case: Mandatory Field Gap
    # ---------------------------------------------------------
    def test_2_missing_complaint_type_gap(self):
        """
        GAP CHECK: Can we save a receipt without a Complaint Type?
        """
        receipt = frappe.get_doc({
            "doctype": "Complaint Receipts",
            "date": today()
        })

        try:
            receipt.insert()
            print("\n[GAP FOUND] System allowed Complaint Receipt WITHOUT Complaint Type!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked receipt without Complaint Type.")

    # ---------------------------------------------------------
    # 3. Behavioral Test Case: Pseudonymous Name Requirement
    # ---------------------------------------------------------
    def test_3_pseudonymous_missing_name_gap(self):
        """
        GAP CHECK: If type is 'Pseudonymous', is 'Complainant Name' mandatory on backend?
        """
        receipt = frappe.get_doc({
            "doctype": "Complaint Receipts",
            "complaint_type": "Pseudonymous",
            "complainant_name": "", 
            "date": today()
        })

        try:
            receipt.insert()
            print("\n[GAP FOUND] Allowed 'Pseudonymous' complaint without a Complainant Name!")
        except ValidationError:
            print("\n[SUCCESS] System correctly required Complainant Name for Pseudonymous type.")

    # ---------------------------------------------------------
    # 4. Logic Test: Past Date Gap
    # ---------------------------------------------------------
    def test_4_highly_backdated_receipt_gap(self):
        """
        GAP CHECK: Does the system allow registering complaints from many years ago?
        """
        receipt = frappe.get_doc({
            "doctype": "Complaint Receipts",
            "complaint_type": "Anonymous",
            "date": "1990-01-01" 
        })

        try:
            receipt.insert()
            print("\n[INFO] System allowed back-dated receipt entry (1990-01-01).")
        except ValidationError:
            print("\n[SUCCESS] System blocked highly back-dated complaints.")

    # ---------------------------------------------------------
    # 5. Proof of Backend Gap (Permanent Save)
    # ---------------------------------------------------------
    def test_5_force_backend_insert_without_name(self):
        """
        FORCE CHECK: Inserting via backend without name to check database acceptance.
        This record will be saved permanently to verify the GAP.
        """
        doc = frappe.get_doc({
            "doctype": "Complaint Receipts",
            "complaint_type": "Pseudonymous",
            "complainant_name": "", # This should be blocked but backend allows it
            "date": today()
        })
        doc.insert(ignore_permissions=True)
        frappe.db.commit() # Permanent Save
        
        print(f"\n[PERMANENT SAVE] Record {doc.name} saved WITHOUT Complainant Name!")

    def tearDown(self):
        """
        ROLLBACK DISABLED to allow checking data in DB/Frontend.
        """
        # frappe.db.rollback() # Commented for verification
        pass