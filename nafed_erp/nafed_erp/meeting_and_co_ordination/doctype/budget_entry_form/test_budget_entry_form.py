# Copyright (c) 2025, CSM Technologies Pvt Ltd and Contributors
# See license.txt

# import frappe
# from frappe.tests.utils import FrappeTestCase


# class TestBudgetEntryForm(FrappeTestCase):
# 	pass

# ===============================================================================================================

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe import ValidationError
from frappe.utils import today

class TestActualBudgetEntryForm(FrappeTestCase):

    def setUp(self):
        """
        Setup dependency: Approved Estimated Budget with all mandatory fields.
        """
        # 1. Fetch existing master IDs to satisfy Link Validation
        self.branch = frappe.db.get_value("Company", {}, "name")
        self.budget_year = frappe.db.get_value("budgetary year", {}, "name")
        self.scheme = frappe.db.get_value("Scheme", {}, "name")
        self.comm_group = frappe.db.get_value("Commodity Type", {}, "name")
        self.iot_branch = frappe.db.get_value("Iot Branch", {}, "name")
        self.commodity = frappe.db.get_value("Commodity", {}, "name")
        self.region = frappe.db.get_value("Zone", {}, "name")
        self.uom = frappe.db.get_value("UOM", {}, "name")

        # 2. Create a fully valid Estimated Budget (Satisfying all mandatory fields)
        self.estimate = frappe.get_doc({
            "doctype": "Estimated Budget Entry Form",
            "branch": self.branch,
            "commodity_group": self.comm_group,
            "export_type": "Direct",
            "scheme": self.scheme,
            "budget_year": self.budget_year,
            "budget_purchase_qty": 1000,
            "budget_sale_qty": 1000,
            "iot_branch": self.iot_branch,
            "commodity": self.commodity,
            "region": self.region,
            "unit_of_measure": self.uom,
            "budget_purchase_value": 500000,
            "budget_sale_value": 600000,
            "budget_export_value": 0,
            "profit": 100000,
            "status": "Approved"
        }).insert(ignore_permissions=True)
        
        # Ensure status is 'Approved' for link_filters in main tests
        frappe.db.set_value("Estimated Budget Entry Form", self.estimate.name, "status", "Approved")
        frappe.db.commit()

    # ---------------------------------------------------------
    # 1. Positive Test Case
    # ---------------------------------------------------------
    def test_1_positive_actual_entry_creation(self):
        """
        CASE 1: Successful creation of an Actual Budget Entry linked to an Estimate.
        """
        actual = frappe.get_doc({
            "doctype": "Budget Entry Form",
            "estimated_budget_form_id": self.estimate.name,
            "budget_purchase_value": 450000, # Within budget
            "status": "Draft"
        })
        actual.insert()
        
        self.assertTrue(frappe.db.exists("Budget Entry Form", actual.name))
        print(f"\n[Positive Test] SUCCESS! Created Actual Entry ID: {actual.name}")

    # ---------------------------------------------------------
    # 2. Negative Test Case: Unapproved Estimate Gap
    # ---------------------------------------------------------
    def test_2_link_filter_gap(self):
        """
        GAP CHECK: Can we link an unapproved (Draft) Estimate?
        """
        # Create a valid Draft estimate with ALL mandatory fields
        draft_estimate = frappe.get_doc({
            "doctype": "Estimated Budget Entry Form",
            "branch": self.branch,
            "commodity_group": self.comm_group,
            "export_type": "Direct",
            "scheme": self.scheme,
            "budget_year": self.budget_year,
            "budget_purchase_qty": 100,
            "budget_sale_qty": 100,
            "iot_branch": self.iot_branch,
            "commodity": self.commodity,
            "region": self.region,
            "unit_of_measure": self.uom,
            "budget_purchase_value": 10000,
            "budget_sale_value": 12000,
            "budget_export_value": 0,
            "profit": 2000,
            "status": "Draft" # ✅ Keep it Draft
        }).insert(ignore_permissions=True)

        actual = frappe.get_doc({
            "doctype": "Budget Entry Form",
            "estimated_budget_form_id": draft_estimate.name,
            "budget_purchase_value": 5000
        })

        try:
            actual.insert()
            # Agar save ho gaya matlab GAP hai
            print("\n[GAP FOUND] Allowed linking to a DRAFT Estimated Budget!")
        except Exception:
            print("\n[SUCCESS] System blocked linking to unapproved estimate.")

    # ---------------------------------------------------------
    # 3. Negative Test Case: Missing Estimate Link Gap
    # ---------------------------------------------------------
    def test_3_missing_estimate_link_gap(self):
        """
        GAP CHECK: Can we save an Actual entry without any Estimate ID? (reqd: 1)
        """
        actual = frappe.get_doc({
            "doctype": "Budget Entry Form",
            "remarks": "Entry without estimate"
        })

        try:
            actual.insert()
            print("\n[GAP FOUND] System allowed Actual Entry WITHOUT an Estimated Budget ID!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked record due to missing link.")

    # ---------------------------------------------------------
    # 4. Behavioral Test: Budget Overrun Check
    # ---------------------------------------------------------
    def test_4_budget_overrun_gap(self):
        """
        GAP CHECK: Does the system allow Actual > Estimated?
        """
        actual = frappe.get_doc({
            "doctype": "Budget Entry Form",
            "estimated_budget_form_id": self.estimate.name,
            "budget_purchase_value": 9000000, # WAY OVER the 500,000 estimate
        })

        try:
            actual.insert()
            # If saved without warning/block, it's a huge financial gap
            print(f"\n[GAP FOUND] System allowed Actual Value ({actual.budget_purchase_value}) to exceed Estimate!")
        except ValidationError:
            print("\n[SUCCESS] System blocked budget overrun.")

    def tearDown(self):
        frappe.db.rollback()