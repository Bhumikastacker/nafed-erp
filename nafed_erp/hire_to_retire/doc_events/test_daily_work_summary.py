import frappe
from frappe.tests.utils import FrappeTestCase
from frappe import ValidationError

class TestDailyWorkSummary(FrappeTestCase):

    def setUp(self):
        """
        Set up pre-requisites: Humein ek Group chahiye summary link karne ke liye.
        """
        self.group_name = "System Testing Group"
        self.user_email = "summary_tester@example.com"

        # 1. Test User create karein
        if not frappe.db.exists("User", self.user_email):
            frappe.get_doc({
                "doctype": "User",
                "email": self.user_email,
                "first_name": "Summary Tester",
                "send_welcome_email": 0
            }).insert(ignore_permissions=True)

        # 2. Daily Work Summary Group create karein (Dependency)
        if not frappe.db.exists("Daily Work Summary Group", self.group_name):
            frappe.get_doc({
                "doctype": "Daily Work Summary Group",
                "name": self.group_name,
                "enabled": 1,
                "users": [{"user": self.user_email}]
            }).insert(ignore_permissions=True)

        frappe.db.commit()

    # ------------------------
    # Positive Test Case
    # ------------------------
    def test_1_positive_summary_creation(self):
        """
        CASE 1: Verify successful creation of Daily Work Summary linked to a group.
        """
        summary = frappe.get_doc({
            "doctype": "Daily Work Summary",
            "daily_work_summary_group": self.group_name,
            "status": "Open"
        })
        summary.insert(ignore_permissions=True)
        self.assertTrue(frappe.db.exists("Daily Work Summary", summary.name))
        print(f"\n[Positive Test] SUCCESS! Summary ID: {summary.name} created for Group: {self.group_name}")

    # ------------------------
    # Negative Test Case (Gap Check)
    # ------------------------
    def test_2_missing_group_gap(self):
        """
        GAP CHECK: Testing if system allows creating a summary without a Group.
        (JSON mein 'daily_work_summary_group' mandatory nahi dikh raha, par logic ke liye zaroori hai)
        """
        summary = frappe.get_doc({
            "doctype": "Daily Work Summary",
            "daily_work_summary_group": None, # INVALID: No group linked
            "status": "Open"
        })

        # Agar system bina group ke summary save kar leta hai, toh yeh ek GAP hai.
        # System ko block karna chahiye kyunki bina group ke email kisko jayega?
        try:
            summary.insert(ignore_permissions=True)
            print("\n[GAP FOUND] Daily Work Summary allowed saving without a Group Link!")
        except Exception:
            print("\n[SUCCESS] System correctly blocked summary without Group.")

    # ------------------------
    # Logic/Default Test Case
    # ------------------------
    def test_3_default_status_check(self):
        """
        LOGIC CHECK: Verify that the default status is 'Open' as per JSON.
        """
        summary = frappe.get_doc({
            "doctype": "Daily Work Summary",
            "daily_work_summary_group": self.group_name
        })
        summary.insert(ignore_permissions=True)

        # JSON mein default "Open" set hai
        self.assertEqual(summary.status, "Open", "Default status should be 'Open'.")
        print(f"[Logic Test] SUCCESS! Initial status is '{summary.status}'")

    def tearDown(self):
        """
        Rollback database changes.
        """
        frappe.db.rollback()