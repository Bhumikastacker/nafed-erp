# Copyright (c) 2026, CSM Technologies Pvt Ltd and Contributors
# See license.txt

# import frappe
# from frappe.tests.utils import FrappeTestCase


# class TestLegalCaseAssignment(FrappeTestCase):
# 	pass

# ========================================================================================================

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe import ValidationError, LinkValidationError

class TestLegalCaseAssignment(FrappeTestCase):

    def setUp(self):
        """
        Setup dependencies: Jurisdiction -> Case Registration and Lawyer.
        """
        # 1. Setup Court/Jurisdiction
        self.jurisdiction = "Delhi High Court"
        if not frappe.db.exists("Jurisdiction", self.jurisdiction):
            frappe.get_doc({"doctype": "Jurisdiction", "name1": self.jurisdiction}).insert(ignore_permissions=True)

        # 2. Setup Branch
        self.branch = "Head Office"
        if not frappe.db.exists("Branch", self.branch):
            frappe.get_doc({"doctype": "Branch", "branch_name": self.branch, "name": self.branch}).insert(ignore_permissions=True)

        # 3. Register a Case
        self.case = frappe.get_doc({
            "doctype": "Legal Case Registration",
            "case_number": "CASE-ASSIGN-001",
            "party_name": "Nafed vs Republic",
            "case_category": "Litigation",
            "jurisdiction": self.jurisdiction,
            "branch_name": self.branch,
            "related_po__contract_ref": "REF-101",
            "agreement_type": "A"
        }).insert(ignore_permissions=True)

        # 4. Setup Lawyer (Legal Advocates)
        self.lawyer_name = "Adv. Rahul Sharma"
        if not frappe.db.exists("Legal Advocates", self.lawyer_name):
            # We create the minimum required as per your previous Legal Advocates JSON
            frappe.get_doc({
                "doctype": "Legal Advocates",
                "name1": self.lawyer_name,
                "phone": "9988776655",
                "mail": "rahul@legal.com",
                "empanelment_status": "Active",
                "max_active_cases": 5,
                "advocate_fee_schedule": "Effective" # Assuming this exists from previous tests
            }).insert(ignore_permissions=True)
            
        frappe.db.commit()

    # ---------------------------------------------------------
    # 1. Positive Test Case
    # ---------------------------------------------------------
    def test_1_positive_assignment(self):
        """
        CASE 1: Verify successful assignment of a case to a lawyer.
        """
        assignment = frappe.get_doc({
            "doctype": "Legal Case Assignment",
            "case_id": self.case.name,
            "lawyer": self.lawyer_name,
            "delegation_status": "Primary"
        })
        assignment.insert()
        
        self.assertTrue(frappe.db.exists("Legal Case Assignment", assignment.name))
        print(f"\n[Positive Test] SUCCESS! Created Assignment ID: {assignment.name}")

    # ---------------------------------------------------------
    # 2. Negative Test Case: Missing Mandatory Fields
    # ---------------------------------------------------------
    def test_2_missing_mandatory_fields_gap(self):
        """
        GAP CHECK: Test if system blocks assignment without Case ID or Lawyer.
        """
        assignment = frappe.get_doc({
            "doctype": "Legal Case Assignment",
            "delegation_status": "Delegated"
            # Missing case_id and lawyer
        })

        try:
            assignment.insert()
            print("\n[GAP FOUND] System allowed Assignment without Case ID or Lawyer!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked assignment due to missing mandatory fields.")

    # ---------------------------------------------------------
    # 3. Negative Test Case: Invalid Link Validation
    # ---------------------------------------------------------
    def test_3_invalid_case_link_gap(self):
        """
        GAP CHECK: Test if system allows assignment for a non-existent Case ID.
        """
        assignment = frappe.get_doc({
            "doctype": "Legal Case Assignment",
            "case_id": "LGL-NON-EXISTENT", # INVALID
            "lawyer": self.lawyer_name,
            "delegation_status": "Primary"
        })

        try:
            assignment.insert()
            print("\n[GAP FOUND] Allowed assignment to a non-existent Case ID!")
        except (LinkValidationError, Exception):
            print("\n[SUCCESS] System correctly blocked invalid Case ID link.")

    # ---------------------------------------------------------
    # 4. Behavioral Test Case: Duplicate Assignment Logic
    # ---------------------------------------------------------
    def test_4_duplicate_assignment_gap(self):
        """
        GAP CHECK: Can the same lawyer be assigned to the same case twice?
        """
        data = {
            "doctype": "Legal Case Assignment",
            "case_id": self.case.name,
            "lawyer": self.lawyer_name,
            "delegation_status": "Primary"
        }
        
        # First assignment
        frappe.get_doc(data).insert()

        # Second assignment attempt
        duplicate = frappe.get_doc(data)
        try:
            duplicate.insert()
            # If it saves, it's a gap because usually one case-one lawyer assignment record is enough
            print("\n[GAP FOUND] System allowed duplicate Assignment for same Case and Lawyer!")
        except Exception:
            print("\n[SUCCESS] System blocked duplicate case assignment.")

    def tearDown(self):
        frappe.db.rollback()