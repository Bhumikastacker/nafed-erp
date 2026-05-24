# Copyright (c) 2025, CSM Technologies Pvt Ltd and Contributors
# See license.txt

# import frappe
# from frappe.tests.utils import FrappeTestCase


# class TestBoardMeeting(FrappeTestCase):
# 	pass

# ================================================================================================================

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe import ValidationError
from frappe.utils import today

class TestMeetingAgenda(FrappeTestCase):

    def setUp(self):
        """
        Setup dependency: Using existing Meeting Type ID from DB.
        """
        # 1. Get an existing Meeting Type ID (Like 'rhat3ggn2t' for AGM)
        # Hum pehle check karenge agar koi bhi record exist karta hai
        self.meeting_type_id = frappe.db.get_value("Meeting Type", {}, "name")
        
        if not self.meeting_type_id:
            # Agar koi record nahi hai, tabhi naya banayenge
            doc = frappe.get_doc({
                "doctype": "Meeting Type",
                "meeting_type": "Annual Board Meeting"
            }).insert(ignore_permissions=True)
            self.meeting_type_id = doc.name

        # 2. Setup a dummy Board Meeting using that ID
        random_hash = frappe.generate_hash(length=4)
        self.meeting_id = f"BM-TEST-{random_hash}"
        
        if not frappe.db.exists("Board Meeting", self.meeting_id):
            frappe.get_doc({
                "doctype": "Board Meeting",
                "meeting_title": "Quarterly Strategy Review",
                "meeting_date": today(),
                "meeting_type": self.meeting_type_id, # ✅ Using real ID
                "venue": "HO Delhi",
                "purpose": "Financial Audit",
                "name": self.meeting_id
            }).insert(ignore_permissions=True)
            
        frappe.db.commit()

    # ---------------------------------------------------------
    # 1. Positive Test Case
    # ---------------------------------------------------------
    def test_1_positive_agenda_creation(self):
        """
        CASE 1: Successful creation of a Meeting Agenda.
        """
        agenda = frappe.get_doc({
            "doctype": "Meeting Agenda",
            "meeting": self.meeting_id,
            "agenda_text": "<p>Review of annual budget and expenditures.</p>",
            "status": "Draft"
        })
        agenda.insert()
        
        self.assertTrue(frappe.db.exists("Meeting Agenda", agenda.name))
        print(f"\n[Positive Test] SUCCESS! Created Agenda ID: {agenda.name}")

    # ---------------------------------------------------------
    # 2. Negative Test Case: Empty Agenda Gap
    # ---------------------------------------------------------
    def test_2_empty_agenda_text_gap(self):
        """
        GAP CHECK: Can we save an agenda without any text content?
        As per JSON, agenda_text is reqd: 1.
        """
        agenda = frappe.get_doc({
            "doctype": "Meeting Agenda",
            "meeting": self.meeting_id,
            "agenda_text": "" # INVALID: Should be blocked
        })

        try:
            agenda.insert()
            # If saved, it's a backend validation gap
            print("\n[GAP FOUND] System allowed saving Meeting Agenda WITHOUT content!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked empty agenda text.")

    # ---------------------------------------------------------
    # 3. Negative Test Case: Missing Meeting Link Gap
    # ---------------------------------------------------------
    def test_3_missing_meeting_link_gap(self):
        """
        GAP CHECK: Can we save an agenda without linking it to a Board Meeting?
        As per JSON, meeting is reqd: 1.
        """
        agenda = frappe.get_doc({
            "doctype": "Meeting Agenda",
            "agenda_text": "<p>Agenda for no meeting.</p>"
            # Missing meeting link
        })

        try:
            agenda.insert()
            print("\n[GAP FOUND] System allowed Agenda WITHOUT a Board Meeting link!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked agenda without parent meeting.")

    # ---------------------------------------------------------
    # 4. Logic Test: Duplicate Meeting Entry
    # ---------------------------------------------------------
    def test_4_duplicate_agenda_for_same_meeting_gap(self):
        """
        GAP CHECK: Does the system allow multiple agenda records for the exact same meeting?
        """
        data = {
            "doctype": "Meeting Agenda",
            "meeting": self.meeting_id,
            "agenda_text": "<p>Initial Agenda Copy</p>"
        }
        
        # First entry
        frappe.get_doc(data).insert()

        # Duplicate attempt
        duplicate = frappe.get_doc(data)
        try:
            duplicate.insert()
            # If saved, it might be a gap in process flow (one meeting should have one consolidated agenda)
            print("\n[GAP FOUND] System allowed DUPLICATE Agenda records for the same Meeting!")
        except Exception:
            print("\n[SUCCESS] System blocked duplicate agenda entry.")

    def tearDown(self):
        frappe.db.rollback()