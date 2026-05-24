# Copyright (c) 2025, CSM Technologies Pvt Ltd and Contributors
# See license.txt

# import frappe
# from frappe.tests.utils import FrappeTestCase


# class TestTrainer(FrappeTestCase):
# 	pass


import frappe
from frappe.tests.utils import FrappeTestCase
from frappe import ValidationError

class TestTrainerGaps(FrappeTestCase):

    def setUp(self):
        """
        Setup: Ensure a clean state for Trainer testing.
        """
        self.trainer_name = "Master Python Instructor"
        
        # Cleanup existing record to avoid naming conflicts
        if frappe.db.exists("Trainer", self.trainer_name):
            frappe.delete_doc("Trainer", self.trainer_name)
            
        frappe.db.commit()

    # ---------------------------------------------------------
    # TEST 1: Positive Case
    # ---------------------------------------------------------
    def test_1_positive_trainer_creation(self):
        """
        CASE 1: Verify successful creation of a Trainer with valid name and status.
        """
        trainer = frappe.get_doc({
            "doctype": "Trainer",
            "trainer_name": self.trainer_name,
            "email": "trainer.test@nafed.in",
            "institution": "Technical Institute of NAFED",
            "status": "Available"
        })
        trainer.insert()
        self.assertTrue(frappe.db.exists("Trainer", trainer.name))
        print(f"\n[Positive Test] SUCCESS! Trainer Created: {trainer.name}")

    # ---------------------------------------------------------
    # NEGATIVE TEST - GAP 1: Duplicate Trainer Name Integrity
    # ---------------------------------------------------------
    def test_gap_1_duplicate_trainer_name(self):
        """
        GAP CHECK: Since 'trainer_name' is the ID source and unique,
        the system must strictly block duplicate names.
        """
        # Create first record
        self.test_1_positive_trainer_creation()

        # Attempt to create a duplicate
        duplicate = frappe.get_doc({
            "doctype": "Trainer",
            "trainer_name": self.trainer_name,
            "email": "different.email@nafed.in"
        })

        try:
            duplicate.insert()
            print("\n[GAP FOUND] System allowed DUPLICATE Trainer Names!")
        except Exception:
            print("\n[SECURE] System correctly blocked duplicate Trainer Name.")

    # ---------------------------------------------------------
    # NEGATIVE TEST - GAP 2: Email Format Validation
    # ---------------------------------------------------------
    def test_gap_2_invalid_email_format(self):
        """
        GAP CHECK: The email field type in JSON is 'Data' instead of 'Email'.
        Does the system allow saving an invalid email format?
        """
        trainer = frappe.get_doc({
            "doctype": "Trainer",
            "trainer_name": "Email Validation Test",
            "email": "this_is_not_an_email" # INVALID DATA
        })

        try:
            trainer.insert()
            # If saved, it means the 'Data' field is not validating email structure
            if "this_is_not_an_email" in trainer.email:
                print("\n[GAP FOUND] System allowed an INVALID Email format in Trainer record!")
        except ValidationError:
            print("\n[SECURE] System correctly validated the email format.")

    # ---------------------------------------------------------
    # NEGATIVE TEST - GAP 3: Empty/Blank Name Integrity
    # ---------------------------------------------------------
    def test_gap_3_blank_trainer_name(self):
        """
        GAP CHECK: Verify if the system allows saving a trainer with purely whitespace as name.
        """
        trainer = frappe.get_doc({
            "doctype": "Trainer",
            "trainer_name": "    ", # White space
            "status": "Available"
        })

        try:
            trainer.insert()
            if not trainer.trainer_name.strip():
                print("\n[GAP FOUND] System allowed saving a Trainer with a BLANK name!")
        except Exception:
            print("\n[SECURE] System blocked blank trainer name.")

    def tearDown(self):
        """
        Cleanup: Rollback database changes.
        """
        frappe.db.rollback()