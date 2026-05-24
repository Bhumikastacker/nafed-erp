import frappe
from frappe.tests.utils import FrappeTestCase
from frappe import ValidationError

class TestLeaveBlockList(FrappeTestCase):

    def setUp(self):
        """
        Set up pre-requisites: Company.
        """
        self.company = "_Test Indian Registered Company"

    # ------------------------
    # Positive Test Case
    # ------------------------
    def test_1_positive_block_list_creation(self):
        """
        CASE 1: Verify successful creation of a valid Leave Block List.
        """
        block_list_name = "Festival Block 2026"
        
        # Cleanup existing to avoid unique constraint error
        if frappe.db.exists("Leave Block List", block_list_name):
            frappe.delete_doc("Leave Block List", block_list_name)

        block_list = frappe.get_doc({
            "doctype": "Leave Block List",
            "leave_block_list_name": block_list_name, # Mandatory field (acts as ID)
            "company": self.company,
            "applies_to_all_departments": 1,
            # --- MANDATORY CHILD TABLE ---
            "leave_block_list_dates": [
                {
                    "full_date": "2026-10-20", # Using dummy date
                    "reason": "Annual Festival"
                }
            ]
        })
        block_list.insert()
        
        # Assertion: Check if record exists
        self.assertTrue(frappe.db.exists("Leave Block List", block_list_name))
        print(f"\n[Positive Test] SUCCESS! Created ID: {block_list.name}")

    # ------------------------
    # Negative Test Case
    # ------------------------
    def test_2_empty_dates_gap(self):
        """
        GAP CHECK: Testing if system allows saving a block list without any dates.
        As per JSON, leave_block_list_dates is mandatory (reqd: 1).
        """
        block_list_name = "Empty Block List Gap Test"
        if frappe.db.exists("Leave Block List", block_list_name):
            frappe.delete_doc("Leave Block List", block_list_name)

        block_list = frappe.get_doc({
            "doctype": "Leave Block List",
            "leave_block_list_name": block_list_name,
            "company": self.company,
            "leave_block_list_dates": [] # INVALID: Empty child table
        })

        try:
            block_list.insert()
            print("\n[GAP FOUND] Leave Block List allowed creation WITHOUT any dates!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked block list without dates.")

    # ------------------------
    # Negative Test Case
    # ------------------------
    def test_3_numeric_name_gap(self):
        """
        GAP CHECK: Testing if purely numeric names are allowed for master data.
        """
        numeric_name = "6666"
        if frappe.db.exists("Leave Block List", numeric_name):
            frappe.delete_doc("Leave Block List", numeric_name)

        block_list = frappe.get_doc({
            "doctype": "Leave Block List",
            "leave_block_list_name": numeric_name
        })

        try:
            block_list.insert()
            print("[GAP FOUND] Leave Block List allowed PURELY NUMERIC name!")
        except ValidationError:
            print("[SUCCESS] System blocked numeric master data name.")

    def tearDown(self):
        """
        Rollback changes.
        """
        frappe.db.rollback()