import frappe
from frappe.tests.utils import FrappeTestCase
from frappe import ValidationError

class TestTaskMilestone(FrappeTestCase):

    def setUp(self):
        """
        Set up pre-requisites: Active and Approved Project.
        """
        self.company = "_Test Company"
        self.project_name = "Milestone Test Project"
        
        # Create a dummy project if not exists (Project must be Approved/Active as per filters)
        if not frappe.db.exists("Project", {"project_name": self.project_name}):
            self.project = frappe.get_doc({
                "doctype": "Project",
                "project_name": self.project_name,
                "status": "Open",
                "is_active": "Yes",
                "custom_approval_status": "Approved", # Mandatory as per your Task link filter
                "expected_start_date": "2026-01-01",
                "expected_end_date": "2026-12-31",
                "estimated_costing":100000,
                "company": "_Test Company"
            }).insert()
        else:
            self.project = frappe.get_last_doc("Project", {"project_name": self.project_name})

    # ------------------------
    # Positive Test Case
    # ------------------------
    def test_1_positive_milestone_creation(self):
        """
        CASE 1: Verify successful creation of a Milestone Task.
        """
        subject = "Phase 1 Completion"
        
        # Cleanup
        frappe.db.delete("Task", {"subject": subject})

        milestone = frappe.get_doc({
            "doctype": "Task",
            "subject": subject,
            "project": self.project.name,
            "is_milestone": 1,
            "is_group": 1, # Milestones are often group tasks
            "status": "Open",
            "exp_start_date": "2026-02-01",
            "exp_end_date": "2026-02-15",
            "custom_estimated_cost": 5000
        })
        milestone.insert()
        
        self.assertTrue(frappe.db.exists("Task", milestone.name))
        print(f"\n[Positive Test] SUCCESS! Created Milestone: {milestone.name}")

    # ------------------------
    # Negative Test Case (Gap Check)
    # ------------------------
    def test_2_milestone_without_subject_gap(self):
        """
        GAP CHECK: Testing if system allows Milestone without Subject (reqd: 1).
        """
        milestone = frappe.get_doc({
            "doctype": "Task",
            "project": self.project.name,
            "is_milestone": 1,
            "exp_start_date": "2026-02-01",
            "exp_end_date": "2026-02-15"
            # Subject is missing
        })

        try:
            milestone.insert()
            print("\n[GAP FOUND] Task allowed creation WITHOUT Subject!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked Task without Subject.")

    # ------------------------
    # Negative Test Case (Dependency Check)
    # ------------------------
    def test_3_invalid_project_filter_gap(self):
        """
        GAP CHECK: Testing if Task allows linking to a non-approved project.
        As per your JSON, project link has filter: custom_approval_status = Approved.
        """
        # Create a rejected project with ALL mandatory fields
        rejected_proj_name = "Rejected Gap Project"
        
        # Cleanup if exists
        if frappe.db.exists("Project", {"project_name": rejected_proj_name}):
            frappe.delete_doc("Project", frappe.get_value("Project", {"project_name": rejected_proj_name}, "name"))

        rejected_proj = frappe.get_doc({
            "doctype": "Project",
            "project_name": rejected_proj_name,
            "custom_approval_status": "Rejected",
            "expected_start_date": "2026-01-01",
            "expected_end_date": "2026-02-01",
            "estimated_costing": 10000,
            "company": self.company
        }).insert()

        milestone = frappe.get_doc({
            "doctype": "Task",
            "subject": "Should Fail Filter Task",
            "project": rejected_proj.name,
            "is_milestone": 1,
            "exp_start_date": "2026-01-05",
            "exp_end_date": "2026-01-10"
        })

        try:
            milestone.insert()
            # Agar insert ho gaya matlab UI filter server-side par validate nahi ho raha (GAP)
            print("\n[GAP FOUND] Task allowed linking to a REJECTED project!")
        except (ValidationError, Exception):
            print("\n[SUCCESS] System blocked linking to invalid project.")

    def tearDown(self):
        frappe.db.rollback()