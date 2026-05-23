import frappe
from frappe.tests.utils import FrappeTestCase
from frappe import ValidationError

class TestEmployeeFeedbackCriteria(FrappeTestCase):

    # ------------------------
    # Positive Test Case
    # ------------------------
    def test_1_positive_criteria_creation(self):
        """
        CASE 1: Verify that a valid Feedback Criteria can be created.
        """
        criteria_name = "Leadership Skills Test"
        
        # Cleanup to ensure a clean test environment
        if frappe.db.exists("Employee Feedback Criteria", criteria_name):
            frappe.delete_doc("Employee Feedback Criteria", criteria_name)

        doc = frappe.get_doc({
            "doctype": "Employee Feedback Criteria",
            "criteria": criteria_name # Mandatory and Unique ID
        })
        doc.insert()
        
        # Assertion: Check if record exists
        self.assertTrue(frappe.db.exists("Employee Feedback Criteria", criteria_name))
        print(f"\n[Positive Test] SUCCESS! Created Criteria: {doc.name}")

    # ------------------------
    # Negative Test Case
    # ------------------------
    def test_2_duplicate_criteria_gap(self):
        """
        GAP CHECK: Verify that the system prevents duplicate Feedback Criteria.
        """
        duplicate_name = "Teamwork"
        
        # Step 1: Create first record
        if not frappe.db.exists("Employee Feedback Criteria", duplicate_name):
            frappe.get_doc({"doctype": "Employee Feedback Criteria", "criteria": duplicate_name}).insert()

        # Step 2: Try to create second record with SAME name
        duplicate_doc = frappe.get_doc({
            "doctype": "Employee Feedback Criteria",
            "criteria": duplicate_name
        })

        try:
            duplicate_doc.insert()
            print("\n[GAP FOUND] System allowed DUPLICATE Employee Feedback Criteria!")
        except frappe.DuplicateEntryError:
            print("\n[SUCCESS] System correctly blocked duplicate criteria name.")

    # ------------------------
    # Negative Test Case
    # ------------------------
    def test_3_numeric_criteria_gap(self):
        """
        GAP CHECK: Testing if purely numeric names are allowed for criteria data.
        """
        numeric_criteria = "5555"
        if frappe.db.exists("Employee Feedback Criteria", numeric_criteria):
            frappe.delete_doc("Employee Feedback Criteria", numeric_criteria)

        doc = frappe.get_doc({
            "doctype": "Employee Feedback Criteria",
            "criteria": numeric_criteria
        })

        try:
            doc.insert()
            print("[GAP FOUND] Employee Feedback Criteria allowed a PURELY NUMERIC name!")
        except ValidationError:
            print("[SUCCESS] System blocked numeric criteria name.")

    def tearDown(self):
        """
        Rollback changes.
        """
        frappe.db.rollback()