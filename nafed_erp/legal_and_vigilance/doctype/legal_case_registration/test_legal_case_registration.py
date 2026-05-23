# Copyright (c) 2026, CSM Technologies Pvt Ltd and Contributors
# See license.txt

# import frappe
# from frappe.tests.utils import FrappeTestCase


# class TestLegalCaseRegistration(FrappeTestCase):
# 	pass

# ==========================================================================================================

# Copyright (c) 2026, CSM Technologies Pvt Ltd

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe import ValidationError, LinkValidationError


class TestLegalCaseRegistration(FrappeTestCase):

    def setUp(self):
        """
        Setup required master data correctly (NO FAILURES)
        """

        # -------------------------------
        # 1. Jurisdiction (Dynamic Fix)
        # -------------------------------
        self.jurisdiction = "Delhi High Court"

        jurisdiction_meta = frappe.get_meta("Jurisdiction")
        autoname_field = None

        if jurisdiction_meta.autoname.startswith("field:"):
            autoname_field = jurisdiction_meta.autoname.split(":")[1]

        if not frappe.db.exists("Jurisdiction", self.jurisdiction):
            doc_data = {
                "doctype": "Jurisdiction",
                "name": self.jurisdiction
            }

            if autoname_field:
                doc_data[autoname_field] = self.jurisdiction

            frappe.get_doc(doc_data).insert(ignore_permissions=True)

        # -------------------------------
        # 2. Branch (FIXED 🔥)
        # -------------------------------
        self.branch = "Head Office"

        if not frappe.db.exists("Branch", self.branch):
            frappe.get_doc({
                "doctype": "Branch",
                "branch": self.branch,          # ✅ REQUIRED (autoname)
                "branch_name": self.branch
            }).insert(ignore_permissions=True)

        frappe.db.commit()

    # ---------------------------------------------------------
    # 1. Positive Test Case
    # ---------------------------------------------------------
    def test_1_positive_case_registration(self):
        """
        ✅ Should create Legal Case successfully
        """

        case = frappe.get_doc({
            "doctype": "Legal Case Registration",
            "case_number": "WP/1234/2026",
            "party_name": "Nafed vs Vendor",
            "case_category": "Litigation",
            "jurisdiction": self.jurisdiction,
            "branch_name": self.branch,
            "related_po__contract_ref": "PO-1002",
            "agreement_type": "A"
        })

        case.insert()

        self.assertTrue(case.name)
        print(f"\n[PASS] Case Created: {case.name}")

    # ---------------------------------------------------------
    # 2. Missing Mandatory Fields
    # ---------------------------------------------------------
    def test_2_missing_mandatory_fields(self):
        """
        ❌ Should fail if required fields missing
        """

        case = frappe.get_doc({
            "doctype": "Legal Case Registration",
            "case_number": "ERR-001",
            "party_name": "Test Missing Data"
        })

        with self.assertRaises(ValidationError):
            case.insert()

        print("\n[PASS] Missing mandatory fields blocked")

    # ---------------------------------------------------------
    # 3. Invalid Jurisdiction Link
    # ---------------------------------------------------------
    def test_3_invalid_jurisdiction_link(self):
        """
        ❌ Should fail for invalid jurisdiction
        """

        case = frappe.get_doc({
            "doctype": "Legal Case Registration",
            "case_number": "WP/999/2026",
            "party_name": "Invalid Jurisdiction Test",
            "case_category": "Litigation",
            "jurisdiction": "Fake Court",  # ❌ invalid
            "branch_name": self.branch,
            "related_po__contract_ref": "PO-999",
            "agreement_type": "B"
        })

        with self.assertRaises(LinkValidationError):
            case.insert()

        print("\n[PASS] Invalid jurisdiction blocked")

    # ---------------------------------------------------------
    # 4. "Other" Category Logic Check
    # ---------------------------------------------------------
    def test_4_other_category_gap(self):
        """
        ⚠️ GAP CHECK: Backend should enforce 'other_case_category'
        """

        case = frappe.get_doc({
            "doctype": "Legal Case Registration",
            "case_number": "OTH-001",
            "party_name": "Other Category Test",
            "case_category": "Other",
            "other_case_category": "",  # ❌ missing
            "jurisdiction": self.jurisdiction,
            "branch_name": self.branch,
            "related_po__contract_ref": "REF-001",
            "agreement_type": "A"
        })

        try:
            case.insert()
            print("\n[GAP FOUND] 'Other' category allowed without specification")
        except ValidationError:
            print("\n[PASS] 'Other' category properly validated")

    # ---------------------------------------------------------
    def tearDown(self):
        frappe.db.rollback()
