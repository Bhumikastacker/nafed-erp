# Copyright (c) 2026, CSM Technologies Pvt Ltd and Contributors
# See license.txt

# import frappe
# from frappe.tests.utils import FrappeTestCase


# class TestBoardCommunication(FrappeTestCase):
# 	pass

# =====================================================================================================================

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe import ValidationError
from frappe.utils import today

class TestBoardCommunication(FrappeTestCase):

    def setUp(self):
        """
        Setup dependencies: Email Template and Member.
        """
        # 1. Setup Email Template (Link filter requires 'Board Communication Template' name)
        self.template_name = "Board Communication Template"
        if not frappe.db.exists("Email Template", self.template_name):
            frappe.get_doc({
                "doctype": "Email Template",
                "name": self.template_name,
                "subject": "Official Board Notification",
                "response_html": "<p>Dear Members, please find the update.</p>"
            }).insert(ignore_permissions=True)

        # 2. Ensure a Member exists for the child table
        self.member_id = frappe.db.get_value("Board Members", {}, "name") or "BOD-001"
        if not frappe.db.exists("Board Members", self.member_id):
            # Using direct SQL as discussed for broken modules
            frappe.db.sql("""INSERT INTO `tabBoard Members` (name, name1) VALUES (%s, %s)""", 
                          (self.member_id, "Test Member"))
            
        frappe.db.commit()

    # ---------------------------------------------------------
    # 1. Positive Test Case
    # ---------------------------------------------------------
    def test_1_positive_communication_creation(self):
        """
        CASE 1: Successful creation of a Board Communication record.
        """
        comm = frappe.get_doc({
            "doctype": "Board Communication",
            "templates": self.template_name,
            "name1": "Monthly Meeting Update",
            "date": today(),
            "message": "<p>Testing valid communication.</p>",
            "status": "Draft",
            "intentend_members": [
                {
                    "member": self.member_id,
                    "attendance": "Present"
                }
            ]
        })
        comm.insert()
        
        self.assertTrue(frappe.db.exists("Board Communication", comm.name))
        print(f"\n[Positive Test] SUCCESS! Created Communication ID: {comm.name}")

    # ---------------------------------------------------------
    # 2. Negative Test Case: Empty Recipient List Gap
    # ---------------------------------------------------------
    def test_2_empty_members_list_gap(self):
        """
        GAP CHECK: Can we save communication without any Intended Members?
        As per JSON, intentend_members is reqd: 1.
        """
        comm = frappe.get_doc({
            "doctype": "Board Communication",
            "templates": self.template_name,
            "name1": "No Recipient Test",
            "date": today(),
            "message": "Message for no one.",
            "intentend_members": [] # INVALID: Empty table
        })

        try:
            comm.insert()
            # If saved, it's a gap. You can't communicate without recipients.
            print("\n[GAP FOUND] System allowed Board Communication WITHOUT any members!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked communication without members.")

    # ---------------------------------------------------------
    # 3. Negative Test Case: Missing Message Gap
    # ---------------------------------------------------------
    def test_3_missing_message_content_gap(self):
        """
        GAP CHECK: Is Message strictly mandatory on backend?
        """
        comm = frappe.get_doc({
            "doctype": "Board Communication",
            "templates": self.template_name,
            "name1": "Missing Content Test",
            "date": today(),
            "intentend_members": [{"member": self.member_id}]
            # Message is missing
        })

        try:
            comm.insert()
            print("\n[GAP FOUND] System allowed saving Communication WITHOUT a message!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked empty message.")

    # ---------------------------------------------------------
    # 4. Logic Test: Invalid Template Link
    # ---------------------------------------------------------
    def test_4_invalid_template_link_gap(self):
        """
        GAP CHECK: Does the system block non-existent Email Templates?
        """
        comm = frappe.get_doc({
            "doctype": "Board Communication",
            "templates": "Fake Template", # INVALID
            "name1": "Template Gap Test",
            "date": today(),
            "message": "Hello",
            "intentend_members": [{"member": self.member_id}]
        })

        try:
            comm.insert()
            print("\n[GAP FOUND] System allowed linking to a non-existent Template!")
        except Exception:
            print("\n[SUCCESS] System correctly blocked invalid template link.")

    def tearDown(self):
        frappe.db.rollback()