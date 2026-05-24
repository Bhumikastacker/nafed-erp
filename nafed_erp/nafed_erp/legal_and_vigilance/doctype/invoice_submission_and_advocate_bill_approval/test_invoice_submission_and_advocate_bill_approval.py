# Copyright (c) 2026, CSM Technologies Pvt Ltd and Contributors
# See license.txt

# import frappe
# from frappe.tests.utils import FrappeTestCase


# class TestInvoiceSubmissionAndAdvocateBillApproval(FrappeTestCase):
# 	pass

# ====================================================================================================

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe import ValidationError, LinkValidationError
from frappe.utils import today

class TestInvoiceSubmission(FrappeTestCase):

    def setUp(self):
        """
        Setup dependencies: Jurisdiction -> Case -> Lawyer -> Bill.
        """
        self.jurisdiction = "Delhi High Court"
        if not frappe.db.exists("Jurisdiction", self.jurisdiction):
            frappe.get_doc({"doctype": "Jurisdiction", "name1": self.jurisdiction}).insert(ignore_permissions=True)

        self.branch = "Head Office"
        if not frappe.db.exists("Branch", self.branch):
            frappe.get_doc({"doctype": "Branch", "branch_name": self.branch, "name": self.branch}).insert(ignore_permissions=True)

        # 1. Setup Case
        self.case = frappe.get_doc({
            "doctype": "Legal Case Registration",
            "case_number": f"BILL-REF-{frappe.generate_hash(length=4)}",
            "party_name": "Billing Test Party",
            "case_category": "Litigation",
            "jurisdiction": self.jurisdiction,
            "branch_name": self.branch,
            "related_po__contract_ref": "REF-BILL",
            "agreement_type": "A"
        }).insert(ignore_permissions=True)

        # 2. Setup Lawyer
        self.lawyer = "Adv. Billing Expert"
        if not frappe.db.exists("Legal Advocates", self.lawyer):
            frappe.get_doc({
                "doctype": "Legal Advocates",
                "name1": self.lawyer,
                "phone": "9955443322",
                "mail": "bill@legal.com",
                "empanelment_status": "Active",
                "max_active_cases": 5,
                "advocate_fee_schedule": "Effective"
            }).insert(ignore_permissions=True)
            
        frappe.db.commit()

    # ---------------------------------------------------------
    # 1. Positive Test Case
    # ---------------------------------------------------------
    def test_1_positive_bill_creation(self):
        """
        CASE 1: Successful creation of Advocate Bill.
        """
        bill = frappe.get_doc({
            "doctype": "Invoice Submission And Advocate Bill Approval",
            "naming_series": "INV-.YY.-",
            "invoice_date": today(),
            "advocate_name": self.lawyer,
            "case_id": self.case.name,
            "fee_type": "Per Hearing Fee",
            "amount": 5000,
            "approval_status": "Pending"
        })
        bill.insert()
        
        self.assertTrue(frappe.db.exists("Invoice Submission And Advocate Bill Approval", bill.name))
        print(f"\n[Positive Test] SUCCESS! Created Bill ID: {bill.name}")

    # ---------------------------------------------------------
    # 2. Negative Test Case: Missing Mandatory Link
    # ---------------------------------------------------------
    def test_2_missing_case_id_gap(self):
        """
        GAP CHECK: Can a bill be saved without a Case ID? (reqd: 1)
        """
        bill = frappe.get_doc({
            "doctype": "Invoice Submission And Advocate Bill Approval",
            "naming_series": "INV-.YY.-",
            "invoice_date": today(),
            "advocate_name": self.lawyer,
            "fee_type": "Consultation Fee",
            "amount": 2000
            # Missing case_id
        })

        try:
            bill.insert()
            print("\n[GAP FOUND] System allowed Bill submission WITHOUT Case ID!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked bill without Case ID.")

    # ---------------------------------------------------------
    # 3. Negative Test Case: Invalid Lawyer Check
    # ---------------------------------------------------------
    def test_3_invalid_advocate_link_gap(self):
        """
        GAP CHECK: Test if system allows linking to a non-existent Lawyer.
        """
        bill = frappe.get_doc({
            "doctype": "Invoice Submission And Advocate Bill Approval",
            "naming_series": "INV-.YY.-",
            "invoice_date": today(),
            "advocate_name": "Ghost Lawyer", # INVALID
            "case_id": self.case.name,
            "fee_type": "Opinion Fee",
            "amount": 10000
        })

        try:
            bill.insert()
            print("\n[GAP FOUND] Allowed bill for a non-existent Advocate!")
        except (LinkValidationError, Exception):
            print("\n[SUCCESS] System correctly blocked invalid Advocate link.")

    # ---------------------------------------------------------
    # 4. Behavioral Test: Duplicate Billing Gap
    # ---------------------------------------------------------
    def test_4_duplicate_invoice_gap(self):
        """
        GAP CHECK: Can the same lawyer submit the exact same bill amount for the same case twice?
        """
        data = {
            "doctype": "Invoice Submission And Advocate Bill Approval",
            "naming_series": "INV-.YY.-",
            "invoice_date": today(),
            "advocate_name": self.lawyer,
            "case_id": self.case.name,
            "fee_type": "Appearance Fee",
            "amount": 7500
        }
        
        frappe.get_doc(data).insert()

        duplicate = frappe.get_doc(data)
        try:
            duplicate.insert()
            # If it saves, it's a gap. Preventing double billing is essential.
            print("\n[GAP FOUND] System allowed DUPLICATE Bill for the same Case and Amount!")
        except Exception:
            print("\n[SUCCESS] System blocked potential duplicate bill.")

    # ---------------------------------------------------------
    # 5. Boundary Test: Zero Amount Gap
    # ---------------------------------------------------------
    def test_5_zero_amount_bill_gap(self):
        """
        GAP CHECK: Is a bill with 0 amount allowed?
        """
        bill = frappe.get_doc({
            "doctype": "Invoice Submission And Advocate Bill Approval",
            "naming_series": "INV-.YY.-",
            "invoice_date": today(),
            "advocate_name": self.lawyer,
            "case_id": self.case.name,
            "fee_type": "Court Fee",
            "amount": 0 # Should ideally be blocked
        })

        try:
            bill.insert()
            print("\n[GAP FOUND] System allowed an Advocate Bill with 0.00 Amount!")
        except (ValidationError, Exception):
            print("\n[SUCCESS] System blocked zero amount billing.")

    def tearDown(self):
        frappe.db.rollback()
