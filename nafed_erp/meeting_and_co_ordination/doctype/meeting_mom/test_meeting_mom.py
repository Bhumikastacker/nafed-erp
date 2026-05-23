# Copyright (c) 2025, CSM Technologies Pvt Ltd and Contributors
# See license.txt

# import frappe
# from frappe.tests.utils import FrappeTestCase


# class TestBoardMeeting(FrappeTestCase):
# 	pass

# ===============================================================================================================

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe import ValidationError
from frappe.utils import today

class TestMeetingMoM(FrappeTestCase):

    def setUp(self):
        """
        Setup dependency: Using existing Meeting Type ID from DB to avoid Link Errors.
        """
        # 1. Fetch an existing Meeting Type ID (Like 'rhat3ggn2t')
        self.meeting_type_id = frappe.db.get_value("Meeting Type", {}, "name")
        
        if not self.meeting_type_id:
            # Only create if absolutely no meeting types exist
            doc = frappe.get_doc({
                "doctype": "Meeting Type",
                "meeting_type": "Standard Board Meeting"
            }).insert(ignore_permissions=True)
            self.meeting_type_id = doc.name

        # 2. Setup a dummy Board Meeting (Force the ID so MoM can find it)
        # We use 'BM-MOM-TEST' as the name to ensure no mismatch
        self.meeting_id = f"BM-MOM-TEST-{frappe.generate_hash(length=4)}"
        
        if not frappe.db.exists("Board Meeting", self.meeting_id):
            frappe.get_doc({
                "doctype": "Board Meeting",
                "meeting_title": "Test Strategic Meet",
                "meeting_date": today(),
                "meeting_type": self.meeting_type_id, # ✅ Use real ID from DB
                "venue": "HO Delhi",
                "purpose": "General Discussion",
                "name": self.meeting_id # ✅ Force Name
            }).insert(ignore_permissions=True)
            
        frappe.db.commit()

    # ---------------------------------------------------------
    # 1. Positive Test Case
    # ---------------------------------------------------------
    def test_1_positive_mom_creation(self):
        """
        CASE 1: Successful creation of Meeting MoM with all mandatory fields.
        """
        mom = frappe.get_doc({
            "doctype": "Meeting MoM",
            "meeting": self.meeting_id,
            "mom_content": "<h3>Meeting Minutes</h3><p>All projects approved.</p>",
            "status": "Draft"
        })
        mom.insert()
        
        self.assertTrue(frappe.db.exists("Meeting MoM", mom.name))
        print(f"\n[Positive Test] SUCCESS! Created MoM ID: {mom.name}")

    # ---------------------------------------------------------
    # 2. Negative Test Case: Empty Content Gap
    # ---------------------------------------------------------
    def test_2_empty_mom_content_gap(self):
        """
        GAP CHECK: Can we save a MoM without any discussion content?
        As per JSON, mom_content is reqd: 1.
        """
        mom = frappe.get_doc({
            "doctype": "Meeting MoM",
            "meeting": self.meeting_id,
            "mom_content": "" # INVALID: Should be blocked
        })

        try:
            mom.insert()
            # If saved, backend validation is missing
            print("\n[GAP FOUND] System allowed saving a Meeting MoM WITHOUT content!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked empty MoM content.")

    # ---------------------------------------------------------
    # 3. Negative Test Case: Orphan MoM Gap
    # ---------------------------------------------------------
    def test_3_missing_meeting_link_gap(self):
        """
        GAP CHECK: Can we save a MoM without linking it to a Board Meeting?
        As per JSON, meeting is reqd: 1.
        """
        mom = frappe.get_doc({
            "doctype": "Meeting MoM",
            "mom_content": "<p>Discussion points.</p>"
            # Missing meeting link
        })

        try:
            mom.insert()
            print("\n[GAP FOUND] System allowed MoM WITHOUT a Board Meeting link!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked MoM without parent meeting.")

    # ---------------------------------------------------------
    # 4. Behavioral Test: Multiple MoM for Same Meeting
    # ---------------------------------------------------------
    def test_4_duplicate_mom_for_same_meeting_gap(self):
        """
        GAP CHECK: Does the system allow creating multiple MoM records for the same meeting?
        """
        data = {
            "doctype": "Meeting MoM",
            "meeting": self.meeting_id,
            "mom_content": "<p>Initial MoM Draft</p>"
        }
        
        # First entry
        frappe.get_doc(data).insert()

        # Duplicate attempt
        duplicate = frappe.get_doc(data)
        try:
            duplicate.insert()
            # Usually, a meeting should have only one final MoM. If it saves, it's a gap.
            print("\n[GAP FOUND] System allowed DUPLICATE MoM records for the same Meeting!")
        except Exception:
            print("\n[SUCCESS] System blocked duplicate MoM entry.")

    def tearDown(self):
        frappe.db.rollback()