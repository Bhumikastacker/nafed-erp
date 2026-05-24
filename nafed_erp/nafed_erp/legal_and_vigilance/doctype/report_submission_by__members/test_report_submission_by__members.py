# Copyright (c) 2026, CSM Technologies Pvt Ltd and Contributors
# See license.txt

# import frappe
# from frappe.tests.utils import FrappeTestCase


# class TestReportSubmissionbyMembers(FrappeTestCase):
# 	pass

# =======================================================================================================

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe import ValidationError
from frappe.utils import today

class TestReportSubmissionByMembers(FrappeTestCase):

    def setUp(self):
        """
        Setup dependency: Complaint Receipt.
        """
        self.receipt = frappe.get_doc({
            "doctype": "Complaint Receipts",
            "complaint_type": "Anonymous",
            "date": today()
        }).insert(ignore_permissions=True)
        
        frappe.db.commit()

    # ---------------------------------------------------------
    # 1. Positive Test Case
    # ---------------------------------------------------------
    def test_1_positive_report_submission(self):
        """
        CASE 1: Successful submission linked to a valid Receipt.
        """
        report = frappe.get_doc({
            "doctype": "Report Submission by  Members",
            "naming_series": "RP-.YYYY.-.####",
            "complaint_receipt": self.receipt.name,
            "remarks": "Member report submitted successfully."
        })
        report.insert()
        
        self.assertTrue(frappe.db.exists("Report Submission by  Members", report.name))
        print(f"\n[Positive Test] SUCCESS! Created Report ID: {report.name}")

    # ---------------------------------------------------------
    # 2. Negative Test Case: Orphan Report Gap
    # ---------------------------------------------------------
    def test_2_orphan_report_gap(self):
        """
        GAP CHECK: Can we submit a report without linking a Complaint Receipt?
        """
        report = frappe.get_doc({
            "doctype": "Report Submission by  Members",
            "remarks": "Ghost report without receipt link"
        })

        try:
            report.insert()
            # If saved, it's a gap. A member report must always belong to a complaint.
            print("\n[GAP FOUND] System allowed Report Submission WITHOUT a Complaint Receipt link!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked report without receipt.")

    # ---------------------------------------------------------
    # 3. Negative Test Case: Empty Content Gap
    # ---------------------------------------------------------
    def test_3_empty_report_gap(self):
        """
        GAP CHECK: Can we save a report with no remarks?
        """
        report = frappe.get_doc({
            "doctype": "Report Submission by  Members",
            "complaint_receipt": self.receipt.name,
            "remarks": "" # Empty editor
        })

        try:
            report.insert()
            print("\n[GAP FOUND] System allowed an EMPTY Report Submission (No Remarks)!")
        except ValidationError:
            print("\n[SUCCESS] System blocked empty report submission.")

    def tearDown(self):
        frappe.db.rollback()
