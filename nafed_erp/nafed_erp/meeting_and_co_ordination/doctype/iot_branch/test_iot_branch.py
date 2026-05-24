# Copyright (c) 2026, CSM Technologies Pvt Ltd and Contributors
# See license.txt

# import frappe
# from frappe.tests.utils import FrappeTestCase


# class TestIotBranch(FrappeTestCase):
# 	pass
# =============================================================================================================

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe import ValidationError

class TestIotBranch(FrappeTestCase):

    # ---------------------------------------------------------
    # 1. Positive Test Case
    # ---------------------------------------------------------
    def test_1_positive_branch_creation(self):
        """
        CASE 1: Successful creation of an IOT Branch.
        """
        branch_name = "IOT Mumbai Central"
        
        # Cleanup if exists
        if frappe.db.exists("Iot Branch", {"name1": branch_name}):
            frappe.db.delete("Iot Branch", {"name1": branch_name})

        branch = frappe.get_doc({
            "doctype": "Iot Branch",
            "name1": branch_name,
            "code": "IOT-MUM-01"
        })
        branch.insert()
        
        self.assertTrue(frappe.db.exists("Iot Branch", branch.name))
        print(f"\n[Positive Test] SUCCESS! Created IOT Branch: {branch.name1}")

    # ---------------------------------------------------------
    # 2. Negative Test Case: Mandatory Name Gap
    # ---------------------------------------------------------
    def test_2_missing_name_gap(self):
        """
        GAP CHECK: Can we save a branch without a Name?
        As per JSON, name1 is reqd: 1.
        """
        branch = frappe.get_doc({
            "doctype": "Iot Branch",
            "code": "ERR-001"
            # Name (name1) is missing
        })

        try:
            branch.insert()
            print("\n[GAP FOUND] System allowed IOT Branch WITHOUT a Name!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked branch without Name.")

    # ---------------------------------------------------------
    # 3. Negative Test Case: Duplicate Branch Gap
    # ---------------------------------------------------------
    def test_3_duplicate_branch_gap(self):
        """
        GAP CHECK: Can two branches have the exact same name?
        Your JSON shows Unique: 0 for name1, which is a potential gap.
        """
        branch_name = "Duplicate Branch Test"
        data = {
            "doctype": "Iot Branch",
            "name1": branch_name,
            "code": "CODE-1"
        }
        
        # Create first
        if not frappe.db.exists("Iot Branch", {"name1": branch_name}):
            frappe.get_doc(data).insert()

        # Try to create second with same name
        duplicate = frappe.get_doc({
            "doctype": "Iot Branch",
            "name1": branch_name,
            "code": "CODE-2"
        })

        try:
            duplicate.insert()
            # If saved, it's a gap in master data integrity
            print(f"\n[GAP FOUND] System allowed DUPLICATE IOT Branch Name: {branch_name}")
        except Exception:
            print("\n[SUCCESS] System blocked duplicate branch name.")

    def tearDown(self):
        frappe.db.rollback()