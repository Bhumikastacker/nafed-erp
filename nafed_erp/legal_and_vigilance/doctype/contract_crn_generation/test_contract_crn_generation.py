# Copyright (c) 2026, CSM Technologies Pvt Ltd and Contributors
# See license.txt

# import frappe
# from frappe.tests.utils import FrappeTestCase


# class TestContractCRNGeneration(FrappeTestCase):
# 	pass

# ========================================================================================================

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe import ValidationError
from frappe.utils import today, add_days

class TestContractCRNGeneration(FrappeTestCase):

    def setUp(self):
        """
        Setup dependencies: Agreement Type and Division with mandatory fields.
        """
        # 1. Setup Agreement Type
        self.agreement_type = "Vendor Agreement"
        if not frappe.db.exists("Agreement Type", self.agreement_type):
            frappe.get_doc({
                "doctype": "Agreement Type",
                "agreement_type": self.agreement_type
            }).insert(ignore_permissions=True)

        # 2. Setup Division (FIXED)
        self.division = "Legal Division"
        if not frappe.db.exists("Division", self.division):
            frappe.get_doc({
                "doctype": "Division",
                "divsion_name": self.division, # Or "divsion_name" if typo exists in your DocType
                "name": self.division           # Adding this to satisfy naming
            }).insert(ignore_permissions=True)
            
        frappe.db.commit()

    # ---------------------------------------------------------
    # 1. Positive Test Case
    # ---------------------------------------------------------
    def test_1_positive_crn_generation(self):
        """
        CASE 1: Successful generation of Contract CRN.
        """
        crn = frappe.get_doc({
            "doctype": "Contract CRN Generation",
            "naming_series": "CRN/.YY./.MM.",
            "agreement_type": self.agreement_type,
            "agreement_title": "Annual Maintenance Contract 2026",
            "date_of_execution": today(),
            "expiry_date": add_days(today(), 365), # 1 year validity
            "division__branch": self.division,
            "purpose": "General Maintenance"
        })
        crn.insert()
        
        self.assertTrue(frappe.db.exists("Contract CRN Generation", crn.name))
        print(f"\n[Positive Test] SUCCESS! Generated CRN: {crn.name}")

    # ---------------------------------------------------------
    # 2. Negative Test Case: Mandatory Field Gap
    # ---------------------------------------------------------
    def test_2_missing_agreement_type_gap(self):
        """
        GAP CHECK: Can we generate a CRN without an Agreement Type? (reqd: 1)
        """
        crn = frappe.get_doc({
            "doctype": "Contract CRN Generation",
            "naming_series": "CRN/.YY./.MM.",
            "agreement_title": "Gap Test Agreement",
            "expiry_date": add_days(today(), 30)
            # Missing agreement_type
        })

        try:
            crn.insert()
            print("\n[GAP FOUND] System allowed CRN generation WITHOUT Agreement Type!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked CRN without Agreement Type.")

    # ---------------------------------------------------------
    # 3. Negative Test Case: Invalid Expiry Date Gap
    # ---------------------------------------------------------
    def test_3_expiry_before_execution_gap(self):
        """
        GAP CHECK: Can Expiry Date be earlier than Date of Execution?
        """
        crn = frappe.get_doc({
            "doctype": "Contract CRN Generation",
            "agreement_type": self.agreement_type,
            "date_of_execution": today(),
            "expiry_date": add_days(today(), -1) # INVALID: Expired yesterday
        })

        try:
            crn.insert()
            # If it saves, it's a gap. A contract shouldn't expire before it's executed.
            print(f"\n[GAP FOUND] System allowed Expiry Date ({crn.expiry_date}) before Execution Date!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked invalid expiry date.")

    # ---------------------------------------------------------
    # 4. Behavioral Test: Past Execution Date
    # ---------------------------------------------------------
    def test_4_past_execution_date_gap(self):
        """
        GAP CHECK: Does the system allow registering contracts executed years ago?
        """
        crn = frappe.get_doc({
            "doctype": "Contract CRN Generation",
            "agreement_type": self.agreement_type,
            "date_of_execution": "2010-01-01", # 16 years ago
            "expiry_date": today()
        })

        try:
            crn.insert()
            # Often allowed for legacy data, but good to know if restricted.
            print("\n[INFO] System allows back-dated contract execution (2010-01-01).")
        except ValidationError:
            print("\n[SUCCESS] System blocked highly back-dated execution.")

    def tearDown(self):
        frappe.db.rollback()
