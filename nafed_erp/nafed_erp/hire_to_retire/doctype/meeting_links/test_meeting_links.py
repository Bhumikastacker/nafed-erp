# Copyright (c) 2025, CSM Technologies Pvt Ltd and Contributors
# See license.txt

# import frappe
# from frappe.tests.utils import FrappeTestCase


# class TestMeetingLinks(FrappeTestCase):
# 	pass


import frappe
from frappe.tests.utils import FrappeTestCase
from frappe import ValidationError

class TestMeetingLinksGaps(FrappeTestCase):

    def setUp(self):
        """
        Setup: Ensure a clean state for Meeting Link testing.
        """
        self.meeting_url = "https://zoom.us/j/123456789"
        self.purpose = "Technical Induction"
        
        # Cleanup existing records to avoid naming collisions based on purpose
        frappe.db.delete("Meeting Links", {"purpose_of_meeting": self.purpose})
        frappe.db.commit()

    # ---------------------------------------------------------
    # TEST 1: Positive Case
    # ---------------------------------------------------------
    def test_1_positive_meeting_link_creation(self):
        """
        CASE 1: Verify successful creation of a meeting link with valid URL and purpose.
        """
        doc = frappe.get_doc({
            "doctype": "Meeting Links",
            "meeting": self.meeting_url,
            "purpose_of_meeting": self.purpose,
            "status": "Active"
        })
        doc.insert()
        self.assertTrue(frappe.db.exists("Meeting Links", doc.name))
        print(f"\n[Positive Test] SUCCESS! Meeting Link Created: {doc.name}")

    # ---------------------------------------------------------
    # NEGATIVE TEST - GAP 1: Duplicate URL Check
    # ---------------------------------------------------------
    def test_gap_1_duplicate_url_integrity(self):
        """
        GAP CHECK: The 'meeting' field is marked as UNIQUE in JSON.
        Does the system strictly prevent two records from using the same URL?
        """
        # Create first record
        self.test_1_positive_meeting_link_creation()

        # Attempt to create a second record with the SAME URL but different purpose
        duplicate = frappe.get_doc({
            "doctype": "Meeting Links",
            "meeting": self.meeting_url, # SAME URL
            "purpose_of_meeting": "Different Purpose"
        })

        try:
            duplicate.insert()
            print("\n[GAP FOUND] System allowed DUPLICATE Meeting URLs!")
        except Exception:
            print("\n[SECURE] System correctly blocked duplicate meeting URL.")

    # ---------------------------------------------------------
    # NEGATIVE TEST - GAP 2: Invalid URL Format
    # ---------------------------------------------------------
    def test_gap_2_invalid_url_format(self):
        """
        GAP CHECK: The 'meeting' field is of type 'Data'. 
        Verify if it allows non-URL strings like 'dummy_text' instead of a real link.
        """
        doc = frappe.get_doc({
            "doctype": "Meeting Links",
            "meeting": "this_is_not_a_link", # INVALID FORMAT
            "purpose_of_meeting": "Invalid URL Test"
        })

        try:
            doc.insert()
            # If saved, it means there is no regex validation for the URL
            if "://" not in doc.meeting:
                print("\n[GAP FOUND] System allowed an INVALID URL format!")
        except ValidationError:
            print("\n[SECURE] System correctly validated the URL format.")

    # ---------------------------------------------------------
    # NEGATIVE TEST - GAP 3: Empty Fields Check
    # ---------------------------------------------------------
    def test_gap_3_blank_meeting_purpose(self):
        """
        GAP CHECK: Does the system allow saving if the meeting link field contains only spaces?
        """
        doc = frappe.get_doc({
            "doctype": "Meeting Links",
            "meeting": "    ", # Only whitespace
            "purpose_of_meeting": "Whitespace Test"
        })

        try:
            doc.insert()
            if not doc.meeting.strip():
                print("\n[GAP FOUND] System allowed a BLANK whitespace Meeting Link!")
        except Exception:
            print("\n[SECURE] System correctly blocked empty link.")

    def tearDown(self):
        """
        Cleanup database changes.
        """
        frappe.db.rollback()