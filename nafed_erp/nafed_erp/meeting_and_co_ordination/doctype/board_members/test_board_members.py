# Copyright (c) 2026, CSM Technologies Pvt Ltd and Contributors
# See license.txt

# import frappe
# from frappe.tests.utils import FrappeTestCase


# class TestBoardMembers(FrappeTestCase):
# 	pass
# ====================================================================================================================

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe import ValidationError
from frappe.utils import today

class TestBoardMembersRegistration(FrappeTestCase):

    def setUp(self):
        """
        Setup dependencies by fetching existing IDs from the database safely.
        """
        # 1. Get an existing AGM Year ID
        self.agm_year = frappe.db.get_value("AGM Year", {}, "name")
        if not self.agm_year:
            self.agm_year = "2025-26"
            frappe.db.sql("INSERT INTO `tabAGM Year` (name) VALUES (%s)", (self.agm_year,))

        # 2. Get an existing Law Code ID
        self.law_code = frappe.db.get_value("Law Code", {}, "name")
        if not self.law_code:
            self.law_code = "LAW-REG-001"
            frappe.db.sql("INSERT INTO `tabLaw Code` (name) VALUES (%s)", (self.law_code,))

        # 3. Get an existing Member Type ID
        self.member_type = frappe.db.get_value("Member Type", {"active": 1}, "name")
        if not self.member_type:
            self.member_type = "Director"
            frappe.db.sql("INSERT INTO `tabMember Type` (name, name1, active) VALUES (%s, %s, %s)", 
                          (self.member_type, self.member_type, 1))
            
        frappe.db.commit()

    # --- POSITIVE TEST ---
    def test_1_positive_registration(self):
        reg = frappe.get_doc({
            "doctype": "Board Members",
            "society_name_1": "Nafed Valid Society",
            "ex_law_code": self.law_code,
            "member_type": self.member_type,
            "agm_year": self.agm_year,
            "mobile": "9876543210",
            "email": "valid@nafed.com"
        })
        reg.insert()
        self.assertTrue(frappe.db.exists("Board Members", reg.name))
        print(f"\n[PASS] Member Registered: {reg.name}")

    # --- MOBILE GAP TESTS ---
    def test_2_mobile_too_short_gap(self):
        """GAP CHECK: Does system block short mobile (e.g. 12)?"""
        reg = frappe.get_doc({
            "doctype": "Board Members",
            "society_name_1": "Short Mobile Test",
            "ex_law_code": self.law_code,
            "member_type": self.member_type,
            "agm_year": self.agm_year,
            "mobile": "12" # INVALID
        })
        try:
            reg.insert()
            print(f"\n[GAP FOUND] System allowed SHORT Mobile No: {reg.mobile}")
        except ValidationError:
            print("\n[SUCCESS] System blocked short mobile number.")

    def test_3_mobile_too_long_gap(self):
        """GAP CHECK: Does system block long mobile (> 10 digits)?"""
        reg = frappe.get_doc({
            "doctype": "Board Members",
            "society_name_1": "Long Mobile Test",
            "ex_law_code": self.law_code,
            "member_type": self.member_type,
            "agm_year": self.agm_year,
            "mobile": "1234567890123" # INVALID
        })
        try:
            reg.insert()
            print(f"\n[GAP FOUND] System allowed LONG Mobile No: {reg.mobile}")
        except ValidationError:
            print("\n[SUCCESS] System blocked long mobile number.")

    # --- EMAIL GAP TEST ---
    def test_4_invalid_email_format_gap(self):
        """GAP CHECK: Does system block incorrect email format?"""
        reg = frappe.get_doc({
            "doctype": "Board Members",
            "society_name_1": "Email Test",
            "ex_law_code": self.law_code,
            "member_type": self.member_type,
            "agm_year": self.agm_year,
            "email": "wrong-email-format" # INVALID
        })
        try:
            reg.insert()
            print(f"\n[GAP FOUND] System allowed INVALID Email Format: {reg.email}")
        except ValidationError:
            print("\n[SUCCESS] System blocked incorrect email format.")

    # --- DUPLICATE GAP TEST ---
    def test_5_duplicate_registration_gap(self):
        """GAP CHECK: Same society same year duplication."""
        data = {
            "doctype": "Board Members",
            "society_name_1": "Duplicate Society",
            "ex_law_code": self.law_code,
            "member_type": self.member_type,
            "agm_year": self.agm_year
        }
        frappe.get_doc(data).insert()
        try:
            frappe.get_doc(data).insert()
            print("\n[GAP FOUND] System allowed DUPLICATE Society Registration!")
        except Exception:
            print("\n[SUCCESS] System blocked duplicate registration.")

    def tearDown(self):
        frappe.db.rollback()
