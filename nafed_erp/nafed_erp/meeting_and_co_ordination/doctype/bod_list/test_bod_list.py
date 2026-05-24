# Copyright (c) 2026, CSM Technologies Pvt Ltd and Contributors
# See license.txt

# import frappe
# from frappe.tests.utils import FrappeTestCase


# class TestBODList(FrappeTestCase):
# 	pass

# ================================================================================================================

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe import ValidationError

class TestBODList(FrappeTestCase):

    def setUp(self):
        """
        Setup dependencies: Meeting Type.
        """
        self.meeting_type = "Annual Board Meeting"
        if not frappe.db.exists("Meeting Type", self.meeting_type):
            frappe.get_doc({
                "doctype": "Meeting Type",
                "meeting_type": self.meeting_type
            }).insert(ignore_permissions=True)
            
        frappe.db.commit()

    # ---------------------------------------------------------
    # 1. Positive Test Case
    # ---------------------------------------------------------
    def test_1_positive_bod_member_creation(self):
        """
        CASE 1: Successful creation of a BOD Member.
        """
        member = frappe.get_doc({
            "doctype": "BOD List",
            "sno": "1",
            "name1": "Mr. Rajesh Khanna",
            "designation": "Director",
            "email": "rajesh@nafed.com",
            "meeting_type": self.meeting_type,
            "committees": "Finance Committee"
        })
        member.insert()
        
        self.assertTrue(frappe.db.exists("BOD List", member.name))
        print(f"\n[Positive Test] SUCCESS! Created BOD Member: {member.name1}")

    # ---------------------------------------------------------
    # 2. Negative Test Case: Empty Record Gap
    # ---------------------------------------------------------
    def test_2_empty_member_record_gap(self):
        """
        GAP CHECK: Does the system allow saving a record with no Name or Email?
        As per JSON, reqd is 0 for name1 and email.
        """
        member = frappe.get_doc({
            "doctype": "BOD List",
            "sno": "99"
            # Name and Email are missing
        })

        try:
            member.insert()
            # If it saves, it's a major data integrity gap
            print("\n[GAP FOUND] System allowed saving a BOD Member WITHOUT Name and Email!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked empty BOD record.")

    # ---------------------------------------------------------
    # 3. Negative Test Case: Duplicate Email Gap
    # ---------------------------------------------------------
    def test_3_duplicate_email_gap(self):
        """
        GAP CHECK: Can two members have the same email address?
        """
        email = "duplicate@bod.com"
        data = {
            "doctype": "BOD List",
            "name1": "Member A",
            "email": email
        }
        frappe.get_doc(data).insert()

        # Attempt to create another with same email
        duplicate = frappe.get_doc({
            "doctype": "BOD List",
            "name1": "Member B",
            "email": email
        })

        try:
            duplicate.insert()
            print(f"\n[GAP FOUND] System allowed DUPLICATE Email for BOD members: {email}")
        except Exception:
            print("\n[SUCCESS] System blocked duplicate BOD email.")

    # ---------------------------------------------------------
    # 4. Negative Test Case: Invalid Email Format
    # ---------------------------------------------------------
    def test_4_invalid_email_format_gap(self):
        """
        GAP CHECK: Does it validate the email format?
        """
        member = frappe.get_doc({
            "doctype": "BOD List",
            "name1": "Invalid Email Test",
            "email": "not-an-email" # INVALID
        })

        try:
            member.insert()
            print(f"\n[GAP FOUND] System allowed INVALID Email format: {member.email}")
        except ValidationError:
            print("\n[SUCCESS] System blocked incorrect BOD email format.")

    def tearDown(self):
        frappe.db.rollback()
