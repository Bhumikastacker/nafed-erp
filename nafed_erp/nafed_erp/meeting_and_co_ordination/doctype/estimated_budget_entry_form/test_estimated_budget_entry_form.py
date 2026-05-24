# Copyright (c) 2026, CSM Technologies Pvt Ltd and Contributors
# See license.txt

# import frappe
# from frappe.tests.utils import FrappeTestCase


# class TestEstimatedBudgetEntryForm(FrappeTestCase):
# 	pass

# ===============================================================================================================

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe import ValidationError

class TestEstimatedBudgetEntryForm(FrappeTestCase):

    def setUp(self):
        """
        Setup dependencies: Branch, Commodity Group, Scheme, Budget Year, IOT Branch, Region, and UOM.
        Using direct SQL or existing records for reliability.
        """
        # 1. Setup Branch (Company)
        self.branch = frappe.db.get_value("Company", {}, "name") or "_Test Company"
        if not frappe.db.exists("Company", self.branch):
            frappe.get_doc({"doctype": "Company", "company_name": self.branch, "default_currency": "INR"}).insert()

        # 2. Setup Commodity Group
        self.comm_group = "Cereals"
        if not frappe.db.exists("Commodity Type", self.comm_group):
            frappe.db.sql("INSERT INTO `tabCommodity Type` (name) VALUES (%s)", (self.comm_group,))

        # 3. Setup Scheme
        self.scheme = "Price Support Scheme"
        if not frappe.db.exists("Scheme", self.scheme):
            frappe.db.sql("INSERT INTO `tabScheme` (name) VALUES (%s)", (self.scheme,))

        # 4. Setup Budgetary Year
        self.budget_year = "2025-2026"
        if not frappe.db.exists("budgetary year", self.budget_year):
            frappe.db.sql("INSERT INTO `tabbudgetary year` (name) VALUES (%s)", (self.budget_year,))

        # 5. Setup IOT Branch
        self.iot_branch = "Mumbai IOT"
        if not frappe.db.exists("Iot Branch", self.iot_branch):
            frappe.db.sql("INSERT INTO `tabIot Branch` (name) VALUES (%s)", (self.iot_branch,))

        # 6. Setup Commodity
        self.commodity = "Moong Dal"
        if not frappe.db.exists("Commodity", self.commodity):
            frappe.db.sql("INSERT INTO `tabCommodity` (name) VALUES (%s)", (self.commodity,))

        # 7. Setup Region (Zone)
        self.region = "West Zone"
        if not frappe.db.exists("Zone", self.region):
            frappe.db.sql("INSERT INTO `tabZone` (name) VALUES (%s)", (self.region,))

        # 8. Setup UOM
        self.uom = "MT"
        if not frappe.db.exists("UOM", self.uom):
            frappe.db.sql("INSERT INTO `tabUOM` (name) VALUES (%s)", (self.uom,))

        frappe.db.commit()

    # ---------------------------------------------------------
    # 1. Positive Test Case
    # ---------------------------------------------------------
    def test_1_positive_budget_estimation(self):
        """
        CASE 1: Successful creation of an Estimated Budget.
        """
        budget = frappe.get_doc({
            "doctype": "Estimated Budget Entry Form",
            "branch": self.branch,
            "commodity_group": self.comm_group,
            "export_type": "Direct Export",
            "scheme": self.scheme,
            "budget_year": self.budget_year,
            "budget_purchase_qty": 500.0,
            "budget_sale_qty": 450.0,
            "iot_branch": self.iot_branch,
            "commodity": self.commodity,
            "region": self.region,
            "unit_of_measure": self.uom,
            "budget_purchase_value": 1000000,
            "budget_sale_value": 1200000,
            "budget_export_value": 0,
            "profit": 200000,
            "status": "Draft"
        })
        budget.insert()
        self.assertTrue(frappe.db.exists("Estimated Budget Entry Form", budget.name))
        print(f"\n[Positive Test] SUCCESS! Created Budget ID: {budget.name}")

    # ---------------------------------------------------------
    # 2. Negative Test Case: Zero/Negative Quantity Gap
    # ---------------------------------------------------------
    def test_2_zero_qty_budget_gap(self):
        """
        GAP CHECK: Does the system allow a budget with 0 Purchase Quantity?
        """
        budget = frappe.get_doc({
            "doctype": "Estimated Budget Entry Form",
            "branch": self.branch,
            "budget_year": self.budget_year,
            "budget_purchase_qty": 0, # INVALID Logic for a budget
            "scheme": self.scheme
        })

        try:
            budget.insert()
            print("\n[GAP FOUND] System allowed an Estimated Budget with ZERO Purchase Quantity!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked zero-quantity budget.")

    # ---------------------------------------------------------
    # 3. Negative Test Case: Profit Logic Gap
    # ---------------------------------------------------------
    def test_3_negative_profit_calculation_gap(self):
        """
        GAP CHECK: Does the system validate that Profit = Sale Value - Purchase Value?
        """
        budget = frappe.get_doc({
            "doctype": "Estimated Budget Entry Form",
            "branch": self.branch,
            "commodity": self.commodity,
            "budget_purchase_value": 1000,
            "budget_sale_value": 500,
            "profit": 2000, # LOGICALLY WRONG: Profit cannot be 2k if sale is less than purchase
            "scheme": self.scheme,
            "budget_year": self.budget_year
        })

        try:
            budget.insert()
            # If it saves without checking the math, it's a gap
            print("\n[GAP FOUND] System allowed invalid Profit calculation!")
        except ValidationError:
            print("\n[SUCCESS] System validated the Profit logic.")

    # ---------------------------------------------------------
    # 4. Mandatory Field Gap
    # ---------------------------------------------------------
    def test_4_missing_masters_gap(self):
        """
        GAP CHECK: Block creation without critical masters (Scheme/Year).
        """
        budget = frappe.get_doc({
            "doctype": "Estimated Budget Entry Form",
            "branch": self.branch,
            "budget_purchase_qty": 100
            # Missing budget_year and scheme
        })

        try:
            budget.insert()
            print("\n[GAP FOUND] System allowed Budget WITHOUT Year or Scheme!")
        except ValidationError:
            print("\n[SUCCESS] System blocked budget due to missing links.")

    def tearDown(self):
        frappe.db.rollback()