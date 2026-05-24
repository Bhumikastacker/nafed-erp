import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import getdate, add_days
from frappe import ValidationError

class TestStaffingPlan(FrappeTestCase):

    def setUp(self):
        """
        Set up pre-requisites: Designation and Company check.
        """
        self.company = "_Test Indian Registered Company"
        self.designation = "Software Engineer"

        # 1. Ensure Designation exists for the child table
        if not frappe.db.exists("Designation", self.designation):
            frappe.get_doc({
                "doctype": "Designation", 
                "designation_name": self.designation
            }).insert()

    def test_1_positive_staffing_plan_creation(self):
        """
        CASE 1 (Positive): Verify that a valid Staffing Plan can be created.
        """
        plan_name = "IT Budget Plan 2026"
        if frappe.db.exists("Staffing Plan", plan_name):
            frappe.delete_doc("Staffing Plan", plan_name)

        staffing_plan = frappe.get_doc({
            "doctype": "Staffing Plan",
            "name": plan_name,               # Required because naming is 'prompt'
            "company": self.company,         # Mandatory
            "from_date": "2026-01-01",       # Mandatory
            "to_date": "2026-12-31",         # Mandatory
            
            # --- MANDATORY CHILD TABLE: staffing_details ---
            "staffing_details": [
                {
                    "designation": self.designation,
                    "vacancies": 5,
                    "estimated_cost_per_position": 50000
                }
            ]
        })
        staffing_plan.insert()
        
        # Assert the record exists
        self.assertTrue(frappe.db.exists("Staffing Plan", plan_name))
        print(f"\n[Positive Test] SUCCESS! Created ID: {staffing_plan.name}")

    def test_2_wrong_date_order_gap(self):
        """
        CASE 2 (Negative): GAP CHECK - Testing if 'To Date' can be before 'From Date'.
        """
        plan_name = "Wrong Date Plan"
        if frappe.db.exists("Staffing Plan", plan_name):
            frappe.delete_doc("Staffing Plan", plan_name)

        staffing_plan = frappe.get_doc({
            "doctype": "Staffing Plan",
            "name": plan_name,
            "company": self.company,
            "from_date": "2026-12-31",
            "to_date": "2026-01-01", # INVALID: To Date is earlier
            "staffing_details": [{"designation": self.designation, "vacancies": 1}]
        })

        try:
            staffing_plan.insert()
            print("\n[GAP FOUND] Staffing Plan allowed invalid date sequence!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked invalid date order.")

    def test_3_empty_details_gap(self):
        """
        CASE 3 (Negative): GAP CHECK - Testing if system allows saving without any rows in Staffing Details.
        JSON says 'reqd: 1' for staffing_details.
        """
        plan_name = "Empty Detail Plan"
        if frappe.db.exists("Staffing Plan", plan_name):
            frappe.delete_doc("Staffing Plan", plan_name)

        staffing_plan = frappe.get_doc({
            "doctype": "Staffing Plan",
            "name": plan_name,
            "company": self.company,
            "from_date": "2026-01-01",
            "to_date": "2026-12-31",
            "staffing_details": [] # GALAT DATA: Empty Child Table
        })

        try:
            staffing_plan.insert()
            print("[GAP FOUND] Staffing Plan allowed creation without any Staffing Details!")
        except ValidationError:
            print("[SUCCESS] System correctly blocked empty staffing details.")

    def tearDown(self):
        """
        Cleanup test data.
        """
        frappe.db.rollback()