import frappe
from frappe.tests.utils import FrappeTestCase
from frappe import ValidationError, MandatoryError

class TestDailyWorkSummaryGroup(FrappeTestCase):

    def setUp(self):
        """
        Set up pre-requisites for Daily Work Summary Group.
        """
        self.user_email = "tester_h2r@example.com"
        self.group_name = "Test Development Group"
        
        # 1. Ensure a Test User exists (needed for the child table 'users')
        if not frappe.db.exists("User", self.user_email):
            frappe.get_doc({
                "doctype": "User",
                "email": self.user_email,
                "first_name": "Test User",
                "send_welcome_email": 0
            }).insert(ignore_permissions=True)

        # 2. Ensure a Holiday List exists (Optional but good for testing)
        if not frappe.db.exists("Holiday List", "Test Holiday List"):
            frappe.get_doc({
                "doctype": "Holiday List",
                "holiday_list_name": "Test Holiday List",
                "from_date": "2024-01-01",
                "to_date": "2024-12-31"
            }).insert(ignore_permissions=True)

        frappe.db.commit()

    # ------------------------
    # Positive Test Case
    # ------------------------
    def test_1_positive_group_creation(self):
        """
        CASE 1: Verify successful creation of a Daily Work Summary Group with users.
        """
        group = frappe.get_doc({
            "doctype": "Daily Work Summary Group",
            "name": self.group_name,
            "enabled": 1,
            "send_emails_at": "18:00",
            "holiday_list": "Test Holiday List",
            "users": [
                {
                    "user": self.user_email
                }
            ]
        })
        group.insert()
        self.assertTrue(frappe.db.exists("Daily Work Summary Group", self.group_name))
        print(f"\n[Positive Test] SUCCESS! Created Group: {group.name}")

    # ------------------------
    # Negative Test Case (Gap Check)
    # ------------------------
    def test_2_empty_users_gap(self):
        """
        GAP CHECK: Testing if system allows creating a group without any users.
        (JSON shows 'users' table as Mandatory 'reqd': 1)
        """
        group = frappe.get_doc({
            "doctype": "Daily Work Summary Group",
            "name": "Empty Group Test",
            "enabled": 1,
            "send_emails_at": "09:00",
            "users": [] # INVALID: Table cannot be empty
        })

        # This test ensures the system blocks groups with no members.
        # If no error is raised, it indicates a functional GAP.
        with self.assertRaises((MandatoryError, ValidationError), msg="GAP FOUND: System allowed saving Group without Users!"):
            group.insert()

    # ------------------------
    # Logic/Default Test Case
    # ------------------------
    def test_3_json_default_values(self):
        """
        LOGIC CHECK: Verify that the system applies default Subject and Message from JSON.
        """
        group = frappe.get_doc({
            "doctype": "Daily Work Summary Group",
            "name": "Default Logic Test",
            "users": [{"user": self.user_email}]
        })
        group.insert()

        # Check if Subject matches JSON default: "What did you work on today?"
        expected_subject = "What did you work on today?"
        self.assertEqual(group.subject, expected_subject, f"Subject should be '{expected_subject}' by default.")
        
        print(f"[Logic Test] SUCCESS! Default subject '{group.subject}' applied correctly.")

    def tearDown(self):
        """
        Rollback database changes.
        """
        frappe.db.rollback()