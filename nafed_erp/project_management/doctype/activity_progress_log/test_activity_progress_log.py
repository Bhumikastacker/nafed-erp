# Copyright (c) 2026, CSM Technologies Pvt Ltd and Contributors
# See license.txt

# import frappe
# from frappe.tests.utils import FrappeTestCase


# class TestActivityProgressLog(FrappeTestCase):
# 	pass

# ===============================================================================================================

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe import ValidationError

class TestActivityProgressLog(FrappeTestCase):

    def setUp(self):
        """
        Set up dependencies with Unique Names using Random Hash.
        """
        self.company = "_Test Company"
        
        # 100% Unique Project Name using Hash
        random_str = frappe.generate_hash(length=8)
        self.project_name = f"Log Test Project {random_str}"
        
        self.tp = "Test Supplier" 
        self.div = "Climate Resilient Innovations"

        # Ensure Supplier and Division exist
        if not frappe.db.exists("Supplier", self.tp):
            frappe.get_doc({"doctype": "Supplier", "supplier_name": self.tp, "supplier_group": "All Supplier Groups"}).insert()
        if not frappe.db.exists("Division", self.div):
            frappe.get_doc({"doctype": "Division", "division_name": self.div, "allow_project_creation": 1}).insert()

        # 1. Create Project
        self.project = frappe.get_doc({
            "doctype": "Project",
            "project_name": self.project_name,
            "status": "Open",
            "is_active": "Yes",
            "custom_approval_status": "Approved",
            "expected_start_date": "2026-01-01",
            "expected_end_date": "2026-12-31",
            "estimated_costing": 100000,
            "company": self.company,
            "custom_division": self.div,
            "custom_technical_partner": self.tp
        }).insert()

        # 2. Create Milestone
        self.milestone = frappe.get_doc({
            "doctype": "Task",
            "subject": f"Milestone {random_str}",
            "project": self.project.name,
            "is_milestone": 1,
            "is_group": 1,
            "task_weight": 100,
            "exp_start_date": "2026-01-01",
            "exp_end_date": "2026-06-01",
            "custom_approval_status": "Approved"
        }).insert()
        frappe.db.set_value("Task", self.milestone.name, "custom_approval_status", "Approved")

        # 3. Create Activity
        self.activity = frappe.get_doc({
            "doctype": "Task",
            "subject": f"Activity {random_str}",
            "project": self.project.name,
            "parent_task": self.milestone.name,
            "is_group": 0,
            "status": "Open",
            "custom_apply_workflow": 1,
            "task_weight": 100,
            "exp_start_date": "2026-01-01",
            "exp_end_date": "2026-02-01",
            "custom_approval_status": "Approved"
        }).insert()
        frappe.db.set_value("Task", self.activity.name, "custom_approval_status", "Approved")
        
        frappe.db.commit()

    def test_1_positive_progress_log_creation(self):
        """
        CASE 1: Success with all mandatory fields.
        """
        log = frappe.get_doc({
            "doctype": "Activity Progress Log",
            "activity": self.activity.name,
            "milestone": self.milestone.name,
            "project": self.project.name,
            "technical_partner": self.tp,
            "division": self.div,
            "activity_progress_percent": 50,
            "actual_start_date": "2026-01-10",
            "actual_end_date": "2026-01-15",
            "remarks": "Completed half task."
        })
        log.insert()
        self.assertTrue(frappe.db.exists("Activity Progress Log", log.name))
        print(f"\n[Positive Test] SUCCESS! Created Log ID: {log.name}")

    def test_2_invalid_date_range_gap(self):
        """
        GAP CHECK: End Date before Start Date.
        """
        log = frappe.get_doc({
            "doctype": "Activity Progress Log",
            "activity": self.activity.name,
            "project": self.project.name,
            "technical_partner": self.tp,
            "division": self.div,
            "activity_progress_percent": 10,
            "actual_start_date": "2026-01-20",
            "actual_end_date": "2026-01-01",
            "remarks": "Testing invalid dates"
        })

        try:
            log.insert()
            print(f"\n[GAP FOUND] Activity Progress Log allowed End Date before Start Date!")
        except (ValidationError, Exception):
            print("\n[SUCCESS] System correctly blocked invalid date range.")

    def test_3_exceeding_progress_percent_gap(self):
        """
        GAP CHECK: Progress > 100%.
        """
        log = frappe.get_doc({
            "doctype": "Activity Progress Log",
            "activity": self.activity.name,
            "project": self.project.name,
            "technical_partner": self.tp,
            "division": self.div,
            "activity_progress_percent": 150,
            "actual_start_date": "2026-01-01",
            "actual_end_date": "2026-01-05",
            "remarks": "Testing over-progress"
        })

        try:
            log.insert()
            print(f"\n[GAP FOUND] Activity Progress Log allowed progress percent as 150%!")
        except (ValidationError, Exception):
            print("\n[SUCCESS] System blocked progress percent > 100%.")

    def tearDown(self):
        frappe.db.rollback()