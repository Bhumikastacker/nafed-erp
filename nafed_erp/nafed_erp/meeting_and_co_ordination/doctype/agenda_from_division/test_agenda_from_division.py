# Copyright (c) 2026, CSM Technologies Pvt Ltd and Contributors
# See license.txt

# import frappe
# from frappe.tests.utils import FrappeTestCase


# class TestAgendaFromDivision(FrappeTestCase):
# 	pass

# ====================================================================================================================

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe import ValidationError
from frappe.utils import today

class TestAgendaFromDivision(FrappeTestCase):

    def setUp(self):
        """
        Setup dependencies by fetching existing records to avoid SQL column errors.
        """
        # 1. Safely get an existing Division ID
        self.division = frappe.db.get_value("Division", {}, "name")
        if not self.division:
            # Fallback if no division exists
            self.division = "Legal Division"
            frappe.db.sql("INSERT INTO `tabDivision` (name) VALUES (%s)", (self.division,))

        # 2. Safely get an existing Meeting Agenda ID
        self.agenda_id = frappe.db.get_value("Meeting Agenda", {}, "name")
        if not self.agenda_id:
            # Fallback: create a meeting first, then agenda
            meeting_name = "MEET-SETUP-001"
            if not frappe.db.exists("Board Meeting", meeting_name):
                frappe.db.sql("INSERT INTO `tabBoard Meeting` (name, status) VALUES (%s, %s)", (meeting_name, "Draft"))
            
            agenda = frappe.get_doc({
                "doctype": "Meeting Agenda",
                "meeting": meeting_name,
                "agenda_text": "Setup Agenda",
                "name": "MA-SETUP-001"
            }).insert(ignore_permissions=True)
            self.agenda_id = agenda.name
            
        frappe.db.commit()

    # ---------------------------------------------------------
    # 1. Positive Test Case
    # ---------------------------------------------------------
    def test_1_positive_division_agenda_creation(self):
        """
        CASE 1: Successful creation of a Division Agenda.
        """
        div_agenda = frappe.get_doc({
            "doctype": "Agenda From Division",
            "agenda_no": self.agenda_id,
            "division": self.division,
            "draft_agenda": "<h3>Division Proposals</h3><p>Proposal for new seed distribution.</p>",
            "from_user": frappe.session.user
        })
        div_agenda.insert()
        
        self.assertTrue(frappe.db.exists("Agenda From Division", div_agenda.name))
        print(f"\n[Positive Test] SUCCESS! Created Division Agenda ID: {div_agenda.name}")

    # ---------------------------------------------------------
    # 2. Negative Test Case: Empty Content Gap
    # ---------------------------------------------------------
    def test_2_empty_draft_agenda_gap(self):
        """
        GAP CHECK: Can we save a division agenda with no text?
        As per JSON, draft_agenda is reqd: 1.
        """
        div_agenda = frappe.get_doc({
            "doctype": "Agenda From Division",
            "agenda_no": self.agenda_id,
            "division": self.division,
            "draft_agenda": "" # INVALID: Empty content
        })

        try:
            div_agenda.insert()
            # If saved, backend validation is missing
            print("\n[GAP FOUND] System allowed saving Division Agenda WITHOUT content!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked empty division agenda.")

    # ---------------------------------------------------------
    # 3. Negative Test Case: Mandatory Link Gap
    # ---------------------------------------------------------
    def test_3_missing_mandatory_links_gap(self):
        """
        GAP CHECK: Can we save without Agenda No or Division?
        """
        div_agenda = frappe.get_doc({
            "doctype": "Agenda From Division",
            "draft_agenda": "Some content here"
            # Missing agenda_no and division
        })

        try:
            div_agenda.insert()
            print("\n[GAP FOUND] System allowed Division Agenda WITHOUT Mandatory Links!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked record due to missing links.")

    # ---------------------------------------------------------
    # 4. Behavioral Test: Cross-Meeting Agenda Link
    # ---------------------------------------------------------
    def test_4_invalid_agenda_no_link_gap(self):
        """
        GAP CHECK: Test if system allows a non-existent Agenda Number.
        """
        div_agenda = frappe.get_doc({
            "doctype": "Agenda From Division",
            "agenda_no": "MA-GHOST-ID", # INVALID
            "division": self.division,
            "draft_agenda": "Valid content"
        })

        try:
            div_agenda.insert()
            print("\n[GAP FOUND] Allowed linking to a non-existent Agenda No!")
        except Exception:
            print("\n[SUCCESS] System correctly blocked invalid Agenda link.")

    def tearDown(self):
        frappe.db.rollback()
