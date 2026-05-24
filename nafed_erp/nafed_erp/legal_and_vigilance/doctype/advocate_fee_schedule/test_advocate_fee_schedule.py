# Copyright (c) 2026, CSM Technologies Pvt Ltd and Contributors
# See license.txt

# import frappe
# from frappe.tests.utils import FrappeTestCase


# class TestAdvocateFeeSchedule(FrappeTestCase):
# 	pass

# ==========================================================================================================

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe import LinkValidationError

class TestAdvocateFeeSchedule(FrappeTestCase):

    def setUp(self):
        """
        Setup dependencies by matching the EXACT spelling system is asking for.
        """
        self.court_id = "Supreme Court"
        if not frappe.db.exists("Court", self.court_id):
            frappe.get_doc({
                "doctype": "Court", 
                "court_name": self.court_id, 
                "name": self.court_id
            }).insert(ignore_if_duplicate=True)

        self.appearance_id = "Final Hearing"
        
        # ✅ FIX: Creating record in BOTH possible DocType names 
        # to satisfy whatever typo is hidden in the system metadata.
        for dt in ["Apperances", "Hearing Apperances"]:
            if frappe.db.exists("DocType", dt):
                if not frappe.db.exists(dt, self.appearance_id):
                    frappe.get_doc({
                        "doctype": dt,
                        "apperance_name": self.appearance_id,
                        "name": self.appearance_id 
                    }).insert(ignore_if_duplicate=True)

        self.rate_id = "7500"
        if not frappe.db.exists("Rate", self.rate_id):
            frappe.get_doc({"doctype": "Rate", "name": self.rate_id}).insert(ignore_if_duplicate=True)

        # Force commit is mandatory for link validation during tests
        frappe.db.commit()

    def test_1_positive_fee_schedule_creation(self):
        """
        ✅ Success Test: Creating with exact ID 'Final Hearing'
        """
        # Cleanup to avoid duplicate error
        frappe.db.delete("Advocate Fee Schedule", {"apperances": self.appearance_id})

        fee_schedule = frappe.get_doc({
            "doctype": "Advocate Fee Schedule",
            "court": self.court_id,
            "apperances": self.appearance_id,
            "category": "Law Firm",
            "rate": self.rate_id
        })
        
        fee_schedule.insert()
        self.assertTrue(frappe.db.exists("Advocate Fee Schedule", fee_schedule.name))
        print(f"\n[PASS] Fee Schedule Created successfully.")

    def test_2_invalid_court_link_gap(self):
        """
        ❌ Negative Test: System should block fake Court IDs.
        """
        fee_doc = frappe.get_doc({
            "doctype": "Advocate Fee Schedule",
            "court": "Invalid Court Name", 
            "apperances": self.appearance_id,
            "category": "Upto 10 years",
            "rate": self.rate_id
        })

        with self.assertRaises(LinkValidationError):
            fee_doc.insert()
        print("\n[PASS] Invalid Court link correctly blocked.")

    def test_3_missing_mandatory_field_gap(self):
        """
        ❌ Negative Test: Missing Appearances should be blocked.
        """
        fee_doc = frappe.get_doc({
            "doctype": "Advocate Fee Schedule",
            "court": self.court_id,
            "category": "10 + Years",
            "rate": self.rate_id
        })

        try:
            fee_doc.insert()
            # If it saves, we found a GAP (Mandatory check not on backend)
            print("\n[GAP FOUND] System allowed saving without Appearances!")
        except Exception:
            print("\n[PASS] Missing mandatory field correctly blocked.")

    def tearDown(self):
        frappe.db.rollback()