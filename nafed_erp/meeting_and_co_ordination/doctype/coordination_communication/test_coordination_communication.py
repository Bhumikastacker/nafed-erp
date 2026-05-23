# Copyright (c) 2026, CSM Technologies Pvt Ltd and Contributors
# See license.txt

# import frappe
# from frappe.tests.utils import FrappeTestCase


# class TestCoordinationCommunication(FrappeTestCase):
# 	pass
# ==============================================================================================================

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe import ValidationError
from frappe.utils import today

class TestCoordinationCommunication(FrappeTestCase):

    def setUp(self):
        """
        Setup dependencies: Email Template.
        """
        # 1. Setup Email Template (Link filter requires 'Board Communication Template' name)
        self.template_name = "Board Communication Template"
        if not frappe.db.exists("Email Template", self.template_name):
            frappe.get_doc({
                "doctype": "Email Template",
                "name": self.template_name,
                "subject": "Coordination Update",
                "response_html": "<p>This is a test coordination message.</p>"
            }).insert(ignore_permissions=True)
            
        frappe.db.commit()

    # ---------------------------------------------------------
    # 1. Positive Test Case
    # ---------------------------------------------------------
    def test_1_positive_coordination_creation(self):
        """
        CASE 1: Successful creation of a Coordination Communication record.
        """
        comm = frappe.get_doc({
            "doctype": "Coordination Communication",
            "templates": self.template_name,
            "name1": "Budget Coordination Subject",
            "date": today(),
            "message": "<p>Valid coordination message content.</p>",
            "send_to": "Division",
            "status": "Draft"
        })
        comm.insert()
        
        self.assertTrue(frappe.db.exists("Coordination Communication", comm.name))
        print(f"\n[Positive Test] SUCCESS! Created Coordination ID: {comm.name}")

    # ---------------------------------------------------------
    # 2. Negative Test Case: Missing Template Gap
    # ---------------------------------------------------------
    def test_2_missing_template_link_gap(self):
        """
        GAP CHECK: Can we save without selecting a Template?
        As per JSON, templates is reqd: 1.
        """
        comm = frappe.get_doc({
            "doctype": "Coordination Communication",
            "name1": "No Template Test",
            "date": today(),
            "message": "Testing without template"
            # Missing templates link
        })

        try:
            comm.insert()
            print("\n[GAP FOUND] System allowed Coordination Communication WITHOUT a Template!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked record without Template.")

    # ---------------------------------------------------------
    # 3. Negative Test Case: Empty Message Gap
    # ---------------------------------------------------------
    def test_3_empty_message_content_gap(self):
        """
        GAP CHECK: Is the Message field strictly mandatory on backend?
        """
        comm = frappe.get_doc({
            "doctype": "Coordination Communication",
            "templates": self.template_name,
            "name1": "Empty Message Test",
            "date": today(),
            "message": "" # INVALID: Should be blocked
        })

        try:
            comm.insert()
            # If saved, it's a gap. You can't send a blank email.
            print("\n[GAP FOUND] System allowed saving Coordination WITHOUT a message!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked empty message.")

    # ---------------------------------------------------------
    # 4. Behavioral Test: Invalid Template Reference
    # ---------------------------------------------------------
    def test_4_invalid_template_link_gap(self):
        """
        GAP CHECK: Test if system allows a non-existent Email Template.
        """
        comm = frappe.get_doc({
            "doctype": "Coordination Communication",
            "templates": "Non-Existent Template", # INVALID
            "name1": "Broken Link Test",
            "date": today(),
            "message": "Hello"
        })

        try:
            comm.insert()
            print("\n[GAP FOUND] Allowed linking to a non-existent Template!")
        except Exception:
            print("\n[SUCCESS] System correctly blocked invalid template link.")

    def tearDown(self):
        frappe.db.rollback()
