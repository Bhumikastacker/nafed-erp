# Copyright (c) 2026, CSM Technologies Pvt Ltd and Contributors
# See license.txt

# import frappe
# from frappe.tests.utils import FrappeTestCase


# class TestLegalCaseHearingOutcome(FrappeTestCase):
# 	pass

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe import ValidationError
from frappe.utils import add_days, today, getdate

class TestLegalCaseHearingOutcome(FrappeTestCase):

    def setUp(self):
        """
        Setup chain: Registration -> Advocate -> Assignment -> Hearing -> Outcome
        """
        self.jurisdiction = "Delhi High Court"
        if not frappe.db.exists("Jurisdiction", self.jurisdiction):
            frappe.get_doc({"doctype": "Jurisdiction", "name1": self.jurisdiction}).insert(ignore_permissions=True)

        self.branch = "Head Office"
        if not frappe.db.exists("Branch", self.branch):
            frappe.get_doc({"doctype": "Branch", "branch_name": self.branch, "name": self.branch}).insert(ignore_permissions=True)

        # 1. Register Case
        self.case = frappe.get_doc({
            "doctype": "Legal Case Registration",
            "case_number": f"OUT-REF-{frappe.generate_hash(length=4)}",
            "party_name": "Outcome Test Party",
            "case_category": "Litigation",
            "jurisdiction": self.jurisdiction,
            "branch_name": self.branch,
            "related_po__contract_ref": "REF-OUT",
            "agreement_type": "A"
        }).insert(ignore_permissions=True)

        # 2. Setup Advocate (Mandatory for Hearing)
        self.advocate_name = "Adv. Fixed Specialist"
        if not frappe.db.exists("Legal Advocates", self.advocate_name):
            frappe.get_doc({
                "doctype": "Legal Advocates",
                "name1": self.advocate_name,
                "phone": "9911223388",
                "mail": "fixed@legal.com",
                "empanelment_status": "Active",
                "max_active_cases": 5,
                "advocate_fee_schedule": "Effective"
            }).insert(ignore_permissions=True)

        # 3. Create Hearing (Now with mandatory Advocate field)
        self.hearing = frappe.get_doc({
            "doctype": "Legal Case Hearing",
            "case_id": self.case.name,
            "hearing_date": today(),
            "hearing_type": "Admission",
            "venue": self.jurisdiction,
            "advocate": self.advocate_name, # ✅ FIXED: Added mandatory field
            "hearing_status": "Pending"
        }).insert(ignore_permissions=True)
            
        frappe.db.commit()

    # ---------------------------------------------------------
    # 1. Positive Test Case
    # ---------------------------------------------------------
    def test_1_positive_outcome_creation(self):
        """
        CASE 1: Successful creation of Hearing Outcome.
        """
        outcome = frappe.get_doc({
            "doctype": "Legal Case Hearing Outcome",
            "case_id": self.case.name,
            "hearing": self.hearing.name,
            "hearing_date": today(),
            "hearing_outcome": "Order reserved by the judge.",
            "awaiting_next_date": 0
        })
        outcome.insert()
        
        self.assertTrue(frappe.db.exists("Legal Case Hearing Outcome", outcome.name))
        print(f"\n[Positive Test] SUCCESS! Created Outcome for Case: {self.case.name}")

    # ---------------------------------------------------------
    # 2. Negative Test Case: Future Outcome Gap
    # ---------------------------------------------------------
    def test_2_future_date_outcome_gap(self):
        """
        GAP CHECK: Can we record an outcome for a future date?
        Result/Outcome cannot happen before the actual date arrives.
        """
        future_date = add_days(today(), 30)
        outcome = frappe.get_doc({
            "doctype": "Legal Case Hearing Outcome",
            "case_id": self.case.name,
            "hearing": self.hearing.name,
            "hearing_date": future_date, # INVALID: Future date
            "hearing_outcome": "Premature result entry"
        })

        try:
            outcome.insert()
            # If saved, it's a gap. You shouldn't know the result of a future hearing.
            print(f"\n[GAP FOUND] System allowed recording Outcome for a FUTURE date ({future_date})!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked future date outcome.")

    # ---------------------------------------------------------
    # 3. Negative Test Case: Orphan Outcome Gap
    # ---------------------------------------------------------
    def test_3_outcome_without_hearing_gap(self):
        """
        GAP CHECK: Can we record an outcome without linking a specific Hearing ID?
        (Your JSON has 'hearing' field as NOT required/reqd:0)
        """
        outcome = frappe.get_doc({
            "doctype": "Legal Case Hearing Outcome",
            "case_id": self.case.name,
            "hearing_date": today(),
            "hearing_outcome": "Ghost Outcome without Hearing ID"
            # Missing hearing link
        })

        try:
            outcome.insert()
            # Since reqd is 0 in JSON, this will likely save, creating data inconsistency.
            print("\n[GAP FOUND] System allowed recording Outcome without linking to a Hearing ID!")
        except Exception:
            print("\n[SUCCESS] System blocked outcome without hearing link.")

    # ---------------------------------------------------------
    # 4. Logic Test: Next Hearing Date Gap
    # ---------------------------------------------------------
    def test_4_missing_next_hearing_date_gap(self):
        """
        GAP CHECK: If 'Awaiting Next Date' is checked, is 'Next Hearing Date' mandatory on backend?
        """
        outcome = frappe.get_doc({
            "doctype": "Legal Case Hearing Outcome",
            "case_id": self.case.name,
            "hearing": self.hearing.name,
            "hearing_date": today(),
            "hearing_outcome": "Next date needed",
            "awaiting_next_date": 1,
            "next_hearing_date": "" # Should be mandatory if awaiting_next_date is 1
        })

        try:
            outcome.insert()
            print("\n[GAP FOUND] Allowed 'Awaiting Next Date' without providing the Date!")
        except Exception:
            print("\n[SUCCESS] System correctly required Next Hearing Date.")

    def tearDown(self):
        frappe.db.rollback()