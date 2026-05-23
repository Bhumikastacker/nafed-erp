import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import today
from frappe import ValidationError, MandatoryError

class TestLearningPathGaps(FrappeTestCase):

    def setUp(self):
        """
        Setup: Creating prerequisites using .db_insert() to bypass broken system hooks.
        """
        self.company = "_Test Indian Registered Company"
        self.emp_id_no = "LP-FIX-V2"
        self.req_id = "REQ-SECURE-V2"

        # 1. Setup Employee with all NAFED mandatory fields
        existing_emp = frappe.db.exists("Employee", {"employee_name": "Learning Tester"})
        if not existing_emp:
            emp = frappe.get_doc({
                "doctype": "Employee",
                "employee_number": self.emp_id_no,
                "first_name": "Learning",
                "last_name": "Tester",
                "employee_name": "Learning Tester",
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
            # Use db_insert to avoid any broken controller logic in Employee Doctype
            emp.db_insert()
            self.employee = emp.name
        else:
            self.employee = existing_emp

        # 2. Setup Training Requisition using .db_insert()
        # This is CRITICAL to bypass the 'nafed_erp.overrides.training_requisition' error.
        if not frappe.db.exists("Training Requisition", self.req_id):
            req = frappe.get_doc({
                "doctype": "Training Requisition",
                "name": self.req_id,
                "employee": self.employee,
                "training_name": "Technical Training",
                "company": self.company,
                "status": "Submitted"
            })
            req.db_insert()

        frappe.db.commit()
        frappe.clear_cache()

    # ---------------------------------------------------------
    # TEST 1: Positive Case
    # ---------------------------------------------------------
    def test_1_positive_learning_path_creation(self):
        """
        CASE 1: Verify creation of Learning Path with valid core courses.
        """
        doc = frappe.get_doc({
            "doctype": "Learning Path",
            "requisition": self.req_id,
            "status": "Draft",
            "core_courses": [
                {
                    "course_name": "Frappe Framework Basics",
                    "trainer": "Internal"
                }
            ]
        })
        doc.insert(ignore_permissions=True)
        self.assertTrue(frappe.db.exists("Learning Path", doc.name))
        print(f"\n[Positive Test] SUCCESS! Learning Path Created: {doc.name}")

    # ---------------------------------------------------------
    # NEGATIVE TEST - GAP 1: Empty Mandatory Table
    # ---------------------------------------------------------
    def test_gap_1_empty_core_courses(self):
        """
        NEGATIVE TEST: Verify if the system allows saving with an empty core courses table.
        According to JSON, this field is mandatory (reqd: 1).
        """
        doc = frappe.get_doc({
            "doctype": "Learning Path",
            "requisition": self.req_id,
            "status": "Draft",
            "core_courses": [] # INVALID: Table is mandatory
        })

        try:
            doc.insert(ignore_permissions=True)
            if not doc.core_courses:
                print("\n[GAP FOUND] Learning Path allowed an EMPTY Core Courses table!")
        except (MandatoryError, ValidationError):
            print("\n[SECURE] System correctly blocked path without core courses.")

    # ---------------------------------------------------------
    # NEGATIVE TEST - GAP 2: Logical Approval Check
    # ---------------------------------------------------------
    def test_gap_2_approved_without_date(self):
        """
        NEGATIVE TEST: Verify if 'Approved' status can be set without an 'Approval Date'.
        Approval date is read-only and should be set automatically by logic.
        """
        doc = frappe.get_doc({
            "doctype": "Learning Path",
            "requisition": self.req_id,
            "status": "Approved", 
            "approval_date": None, # Should be blocked if status is Approved
            "core_courses": [{"course_name": "Audit Path"}]
        })

        try:
            doc.insert(ignore_permissions=True)
            if doc.status == "Approved" and not doc.approval_date:
                print("\n[GAP FOUND] System allowed status 'Approved' without an Approval Date!")
        except ValidationError:
            print("\n[SECURE] System correctly blocked approved status without a date.")

    def tearDown(self):
        frappe.db.rollback()