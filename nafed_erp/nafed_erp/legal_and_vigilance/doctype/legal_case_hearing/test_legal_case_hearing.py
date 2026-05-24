# Copyright (c) 2026, CSM Technologies Pvt Ltd and Contributors
# See license.txt

# import frappe
# from frappe.tests.utils import FrappeTestCase


# class TestLegalCaseHearing(FrappeTestCase):
# 	pass

# =========================================================================================================

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe import ValidationError
from frappe.utils import add_days, today, getdate

class TestLegalCaseHearing(FrappeTestCase):

    def setUp(self):
        """
        Setup chain: Jurisdiction -> Case -> Assignment -> Hearing.
        """
        # 1. Setup Court
        self.jurisdiction = "Delhi High Court"
        if not frappe.db.exists("Jurisdiction", self.jurisdiction):
            frappe.get_doc({"doctype": "Jurisdiction", "name1": self.jurisdiction}).insert(ignore_permissions=True)

        # 2. Setup Branch
        self.branch = "Head Office"
        if not frappe.db.exists("Branch", self.branch):
            frappe.get_doc({"doctype": "Branch", "branch_name": self.branch, "name": self.branch}).insert(ignore_permissions=True)

        # 3. Register Case
        self.case = frappe.get_doc({
            "doctype": "Legal Case Registration",
            "case_number": f"HEAR-REF-{frappe.generate_hash(length=4)}",
            "party_name": "Nafed Test Party",
            "case_category": "Litigation",
            "jurisdiction": self.jurisdiction,
            "branch_name": self.branch,
            "related_po__contract_ref": "REF-HEAR",
            "agreement_type": "A"
        }).insert(ignore_permissions=True)

        # 4. Setup Advocate & Assignment
        self.lawyer = "Adv. Hearing Specialist"
        if not frappe.db.exists("Legal Advocates", self.lawyer):
            frappe.get_doc({
                "doctype": "Legal Advocates",
                "name1": self.lawyer,
                "phone": "9911223344",
                "mail": "hear@legal.com",
                "empanelment_status": "Active",
                "max_active_cases": 5,
                "advocate_fee_schedule": "Effective"
            }).insert(ignore_permissions=True)

        self.assignment = frappe.get_doc({
            "doctype": "Legal Case Assignment",
            "case_id": self.case.name,
            "lawyer": self.lawyer,
            "delegation_status": "Primary"
        }).insert(ignore_permissions=True)
            
        frappe.db.commit()

    # ---------------------------------------------------------
    # 1. Positive Test Case
    # ---------------------------------------------------------
    def test_1_positive_hearing_creation(self):
        """
        CASE 1: Successful creation of a Hearing.
        """
        hearing = frappe.get_doc({
            "doctype": "Legal Case Hearing",
            "case_id": self.case.name,
            "hearing_date": add_days(today(), 7), # Next week
            "hearing_type": "Admission",
            "venue": self.jurisdiction,
            "advocate": self.lawyer,
            "hearing_status": "Pending",
            "ref": self.assignment.name
        })
        hearing.insert()
        
        self.assertTrue(frappe.db.exists("Legal Case Hearing", hearing.name))
        print(f"\n[Positive Test] SUCCESS! Created Hearing ID: {hearing.name}")

    # ---------------------------------------------------------
    # 2. Negative Test Case: Past Date Gap
    # ---------------------------------------------------------
    def test_2_past_date_hearing_gap(self):
        """
        GAP CHECK: Can we schedule a hearing in the past?
        """
        hearing = frappe.get_doc({
            "doctype": "Legal Case Hearing",
            "case_id": self.case.name,
            "hearing_date": "2000-01-01", # INVALID: Far in the past
            "hearing_type": "Final",
            "venue": self.jurisdiction,
            "advocate": self.lawyer,
            "hearing_status": "Pending"
        })

        try:
            hearing.insert()
            # If saves, it's a gap. Future hearings shouldn't be backdated easily.
            print("\n[GAP FOUND] System allowed scheduling a Hearing in the PAST (2000-01-01)!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked past date hearing.")

    # ---------------------------------------------------------
    # 3. Negative Test Case: Unassigned Case Gap
    # ---------------------------------------------------------
    def test_3_unassigned_case_hearing_gap(self):
        """
        GAP CHECK: Can we create a hearing for a case not yet assigned to an advocate?
        """
        # Create a new unassigned case
        unassigned_case = frappe.get_doc({
            "doctype": "Legal Case Registration",
            "case_number": "UNASSIGNED-001",
            "party_name": "No Lawyer Yet",
            "case_category": "Litigation",
            "jurisdiction": self.jurisdiction,
            "branch_name": self.branch,
            "related_po__contract_ref": "REF-NONE",
            "agreement_type": "B"
        }).insert(ignore_permissions=True)

        hearing = frappe.get_doc({
            "doctype": "Legal Case Hearing",
            "case_id": unassigned_case.name,
            "hearing_date": add_days(today(), 1),
            "hearing_type": "Argument",
            "venue": self.jurisdiction,
            "advocate": "Random Lawyer", # Not assigned to this case
            "hearing_status": "Pending"
        })

        try:
            hearing.insert()
            print("\n[GAP FOUND] Allowed hearing for a Case not officially assigned to this Lawyer!")
        except Exception:
            print("\n[SUCCESS] System blocked hearing for unassigned case/advocate.")

    # ---------------------------------------------------------
    # 4. Mandatory Field Gap
    # ---------------------------------------------------------
    def test_4_missing_venue_gap(self):
        """
        GAP CHECK: Testing if Venue (Court) is strictly mandatory on backend.
        """
        hearing = frappe.get_doc({
            "doctype": "Legal Case Hearing",
            "case_id": self.case.name,
            "hearing_date": today(),
            "hearing_type": "Final",
            "advocate": self.lawyer,
            "hearing_status": "Pending"
            # Missing Venue
        })

        try:
            hearing.insert()
            print("\n[GAP FOUND] System allowed Hearing WITHOUT a Venue/Court!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked hearing without Venue.")

    def tearDown(self):
        frappe.db.rollback()