import frappe
from frappe.tests.utils import FrappeTestCase
from frappe import ValidationError, MandatoryError

class TestNafedMilestonesGaps(FrappeTestCase):

    def setUp(self):
        """
        Setup: Ensure a clean state for Milestone testing.
        """
        self.milestone_title = "Technical Certification 2026"
        
        # Cleanup existing record with same title to avoid Naming Collision
        if frappe.db.exists("Nafed Milestones", self.milestone_title):
            frappe.delete_doc("Nafed Milestones", self.milestone_title)
            
        frappe.db.commit()

    # ---------------------------------------------------------
    # TEST 1: Positive Case
    # ---------------------------------------------------------
    def test_1_positive_milestone_creation(self):
        """
        CASE 1: Verify successful creation of a Milestone with valid title and child table data.
        """
        doc = frappe.get_doc({
            "doctype": "Nafed Milestones",
            "milestone_title": self.milestone_title,
            "overall_progress": 50.0,
            "expected_average_rating": 4,
            "table_nxqn": [
                {
                    "step_name": "Phase 1: Basics", # Assuming standard field name
                    "status": "Completed"
                }
            ]
        })
        doc.insert()
        self.assertTrue(frappe.db.exists("Nafed Milestones", doc.name))
        print(f"\n[Positive Test] SUCCESS! Milestone '{doc.name}' created.")

    # ---------------------------------------------------------
    # NEGATIVE TEST - GAP 1: Percentage Overflow (> 100%)
    # ---------------------------------------------------------
    def test_gap_1_progress_percentage_overflow(self):
        """
        GAP CHECK: Does the system allow 'Overall Progress' to exceed 100%?
        Logically, progress cannot be 150%.
        """
        doc = frappe.get_doc({
            "doctype": "Nafed Milestones",
            "milestone_title": "Percentage Gap Test",
            "overall_progress": 150.0, # INVALID: Exceeds 100%
            "table_nxqn": [{"step_name": "Overflow Test"}]
        })

        try:
            doc.insert()
            if doc.overall_progress > 100:
                print("\n[GAP FOUND] System allowed Progress Percentage to exceed 100%!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked percentage overflow.")

    # ---------------------------------------------------------
    # NEGATIVE TEST - GAP 2: Negative Progress Check
    # ---------------------------------------------------------
    def test_gap_2_negative_progress(self):
        """
        GAP CHECK: Does the system allow a negative value in the Progress field?
        """
        doc = frappe.get_doc({
            "doctype": "Nafed Milestones",
            "milestone_title": "Negative Progress Test",
            "overall_progress": -20.0, # INVALID
            "table_nxqn": [{"step_name": "Negative Test"}]
        })

        try:
            doc.insert()
            if doc.overall_progress < 0:
                print("\n[GAP FOUND] System allowed a NEGATIVE Progress Percentage!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked negative progress.")

    # ---------------------------------------------------------
    # NEGATIVE TEST - GAP 3: Empty Mandatory Table
    # ---------------------------------------------------------
    def test_gap_3_empty_steps_table(self):
        """
        GAP CHECK: The child table 'table_nxqn' is mandatory (reqd: 1).
        Does the backend strictly prevent saving a Milestone with zero steps?
        """
        doc = frappe.get_doc({
            "doctype": "Nafed Milestones",
            "milestone_title": "Empty Table Test",
            "overall_progress": 0,
            "table_nxqn": [] # INVALID: Table is required
        })

        try:
            doc.insert()
            if not doc.table_nxqn:
                print("\n[GAP FOUND] System allowed saving a Milestone with an EMPTY child table!")
        except (MandatoryError, ValidationError):
            print("\n[SUCCESS] System correctly enforced mandatory child table.")

    def tearDown(self):
        """
        Cleanup: Rollback dummy data.
        """
        frappe.db.rollback()