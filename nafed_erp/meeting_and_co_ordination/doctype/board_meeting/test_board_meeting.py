# Copyright (c) 2025, CSM Technologies Pvt Ltd and Contributors
# See license.txt

# import frappe
# from frappe.tests.utils import FrappeTestCase


# class TestBoardMeeting(FrappeTestCase):
# 	pass

# ====================================================================================================================

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe import ValidationError
from frappe.utils import today, nowtime, add_days

class TestBoardMeeting(FrappeTestCase):

    def setUp(self):
        """
        Setup dependencies: Meeting Type.
        """
        # Get an existing Meeting Type ID or create one
        self.meeting_type_id = frappe.db.get_value("Meeting Type", {}, "name")
        
        if not self.meeting_type_id:
            doc = frappe.get_doc({
                "doctype": "Meeting Type",
                "meeting_type": "Annual General Meeting"
            }).insert(ignore_permissions=True)
            self.meeting_type_id = doc.name
            
        frappe.db.commit()

    # ---------------------------------------------------------
    # 1. Positive Test Case
    # ---------------------------------------------------------
    def test_1_positive_meeting_creation(self):
        """
        CASE 1: Successful creation of a Board Meeting with all mandatory fields.
        """
        meeting = frappe.get_doc({
            "doctype": "Board Meeting",
            "meeting_type": self.meeting_type_id,
            "meeting_date": today(),
            "meeting_time": nowtime(),
            "venue": "Conference Hall A",
            "purpose": "Monthly review of projects.",
            "status": "Draft"
        })
        meeting.insert()
        
        self.assertTrue(frappe.db.exists("Board Meeting", meeting.name))
        print(f"\n[Positive Test] SUCCESS! Created Board Meeting ID: {meeting.name}")

    # ---------------------------------------------------------
    # 2. Negative Test Case: Empty Attendance Gap
    # ---------------------------------------------------------
    def test_2_empty_attendance_gap(self):
        """
        GAP CHECK: Can a meeting be saved without any attendees?
        (Usually, a meeting requires at least one person).
        """
        meeting = frappe.get_doc({
            "doctype": "Board Meeting",
            "meeting_type": self.meeting_type_id,
            "meeting_date": today(),
            "meeting_time": nowtime(),
            "venue": "Room 101",
            "purpose": "Test without members",
            "attendance": [] # Empty child table
        })

        try:
            meeting.insert()
            # If saved, it's a process gap
            print("\n[GAP FOUND] System allowed saving a Meeting WITHOUT any Attendance members!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked meeting without attendance.")

    # ---------------------------------------------------------
    # 3. Negative Test Case: Past Date Gap
    # ---------------------------------------------------------
    def test_3_past_date_meeting_gap(self):
        """
        GAP CHECK: Can we schedule a meeting in the far past?
        """
        past_date = "2010-01-01"
        meeting = frappe.get_doc({
            "doctype": "Board Meeting",
            "meeting_type": self.meeting_type_id,
            "meeting_date": past_date, # INVALID: 16 years ago
            "meeting_time": nowtime(),
            "venue": "Old Office",
            "purpose": "History test"
        })

        try:
            meeting.insert()
            print(f"\n[GAP FOUND] System allowed a Board Meeting in the PAST ({past_date})!")
        except ValidationError:
            print("\n[SUCCESS] System blocked back-dated meeting.")

    # ---------------------------------------------------------
    # 4. Mandatory Field Gap
    # ---------------------------------------------------------
    def test_4_missing_purpose_gap(self):
        """
        GAP CHECK: Is Purpose strictly required on backend?
        """
        meeting = frappe.get_doc({
            "doctype": "Board Meeting",
            "meeting_type": self.meeting_type_id,
            "meeting_date": today(),
            "meeting_time": nowtime(),
            "venue": "HO"
            # Missing Purpose
        })

        try:
            meeting.insert()
            print("\n[GAP FOUND] System allowed Meeting WITHOUT a Purpose!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked meeting without purpose.")

    def tearDown(self):
        frappe.db.rollback()