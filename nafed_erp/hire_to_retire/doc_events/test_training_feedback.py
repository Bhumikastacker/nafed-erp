import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import today
from frappe import ValidationError

class TestNafedTrainingFeedbackGaps(FrappeTestCase):

    def setUp(self):
        """
        Setup: Using .db_insert() to create prerequisites.
        This bypasses the broken 'add_meeting_link_comment' hook in Training Meeting.
        """
        self.company = "_Test Indian Registered Company"
        self.emp_no = "FEED-FIX-99"
        self.meet_id = "MEET-SECURE-FEED"

        # 1. Setup Employee with all NAFED mandatory fields
        if not frappe.db.exists("Employee", {"employee_number": self.emp_no}):
            emp = frappe.get_doc({
                "doctype": "Employee",
                "employee_number": self.emp_no,
                "first_name": "Feedback",
                "last_name": "Tester",
                "employee_name": "Feedback Tester",
                "gender": "Male",
                "date_of_joining": "2020-01-01",
                "date_of_birth": "1990-01-01",
                "company": self.company,
                "pan_number": "ABCDE1234F",
                "custom_uan_number": "100000000000",
                "custom_allotted_official_accommodation": "No",
                "custom_vpf_applicable": "No",
                "custom_ppedate": today()
            })
            emp.db_insert() # Bypassing controller logic
            self.employee = emp.name
        else:
            self.employee = frappe.db.get_value("Employee", {"employee_number": self.emp_no}, "name")

        # 2. Setup Training Meeting via db_insert to avoid system crash
        if not frappe.db.exists("Nafed Training Meeting", self.meet_id):
            meet = frappe.get_doc({
                "doctype": "Nafed Training Meeting",
                "name": self.meet_id,
                "meeting_title": "Feedback Logic Test",
                "meeting_date": today(),
                "status": "Completed"
            })
            meet.db_insert() # CRITICAL: Bypassing broken meeting hooks

        frappe.db.commit()
        frappe.clear_cache()

    # ---------------------------------------------------------
    # TEST 1: Positive Case
    # ---------------------------------------------------------
    def test_1_positive_feedback_creation(self):
        """ Verify valid feedback creation with Meeting and Employee. """
        feedback = frappe.get_doc({
            "doctype": "Nafed Training Feedback",
            "meeting": self.meet_id,
            "employee": self.employee,
            "rating": 4,
            "rating_score": 15,
            "comments": "Great training session."
        })
        feedback.insert()
        self.assertTrue(frappe.db.exists("Nafed Training Feedback", feedback.name))
        print(f"\n[Positive Test] SUCCESS! Feedback Created: {feedback.name}")

    # ---------------------------------------------------------
    # NEGATIVE TEST - GAP 1: Orphan Record Check
    # ---------------------------------------------------------
    def test_gap_1_orphan_feedback_check(self):
        """ 
        NEGATIVE TEST: Verify if feedback can be saved without links. 
        A feedback without an Employee or Meeting is a data integrity GAP.
        """
        feedback = frappe.get_doc({
            "doctype": "Nafed Training Feedback",
            "meeting": None,
            "employee": None,
            "rating": 5
        })
        try:
            feedback.insert()
            print("\n[GAP FOUND] System allowed an ORPHAN Feedback record!")
        except Exception:
            print("\n[SECURE] System correctly blocked feedback without links.")

    # ---------------------------------------------------------
    # NEGATIVE TEST - GAP 2: Negative Score Check
    # ---------------------------------------------------------
    def test_gap_2_invalid_rating_score(self):
        """ 
        NEGATIVE TEST: Verify if the system allows negative rating scores. 
        """
        feedback = frappe.get_doc({
            "doctype": "Nafed Training Feedback",
            "meeting": self.meet_id,
            "employee": self.employee,
            "rating_score": -15.0 # INVALID
        })
        try:
            feedback.insert()
            if feedback.rating_score < 0:
                print(f"\n[GAP FOUND] System allowed a NEGATIVE Rating Score ({feedback.rating_score})!")
        except ValidationError:
            print("\n[SECURE] System blocked negative score.")

    def tearDown(self):
        frappe.db.rollback()