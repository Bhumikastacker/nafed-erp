import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import getdate, today, add_days
from frappe import ValidationError

class TestAppraisal(FrappeTestCase):

    def setUp(self):
        """
        Setup: Force updating the employee record to satisfy the 'Reports To' validation.
        """
        self.company = "_Test Indian Registered Company"
        
        # 1. Create a Manager/Reporting Officer first
        if not frappe.db.exists("Employee", {"first_name": "ManagerUser"}):
            mgr = frappe.get_doc({
                "doctype": "Employee",
                "employee_number": "EMP-MGR-001",
                "first_name": "ManagerUser",
                "gender": "Male",
                "date_of_joining": "2015-01-01",
                "status": "Active",
                "company": self.company
            }).insert(ignore_mandatory=True)
            self.manager_id = mgr.name
        else:
            self.manager_id = frappe.db.get_value("Employee", {"first_name": "ManagerUser"}, "name")

        # 2. Create/Get the Appraisal User
        if not frappe.db.exists("Employee", {"first_name": "AppraisalUser"}):
            emp = frappe.get_doc({
                "doctype": "Employee",
                "employee_number": "EMP-APR-001",
                "first_name": "AppraisalUser",
                "gender": "Male",
                "date_of_joining": "2024-01-01",
                "status": "Active",
                "company": self.company,
                "reports_to": self.manager_id, # Link manager
                "date_of_birth": "1990-01-01",
                "custom_vpf_applicable": "No"
            }).insert(ignore_mandatory=True)
            self.employee = emp.name
        else:
            self.employee = frappe.db.get_value("Employee", {"first_name": "AppraisalUser"}, "name")
            # FORCE FIX: Update reports_to officer to bypass the validation error
            frappe.db.set_value("Employee", self.employee, "reports_to", self.manager_id)

        # 3. Setup Template and Cycle
        if not frappe.db.exists("Appraisal Template", "Standard Appraisal Template"):
            frappe.get_doc({
                "doctype": "Appraisal Template",
                "template_title": "Standard Appraisal Template",
                "goals": [{"kra": "KRA 1", "per_weightage": 100}],
                "rating_criteria": [{"feedback_criteria": "Technical", "per_weightage": 100}]
            }).insert(ignore_mandatory=True)

        if not frappe.db.exists("Appraisal Cycle", "Standard Cycle 2026"):
            frappe.get_doc({
                "doctype": "Appraisal Cycle",
                "cycle_name": "Standard Cycle 2026",
                "company": self.company,
                "start_date": "2026-01-01",
                "end_date": "2026-12-31"
            }).insert()

        # Database commit taaki changes validation ko dikhein
        frappe.db.commit()

    def test_1_positive_appraisal_creation(self):
        """Positive Case: Verify valid creation of Appraisal."""
        appraisal = frappe.get_doc({
            "doctype": "Appraisal",
            "naming_series": "HR-APR-.YYYY.-",
            "employee": self.employee,
            "company": self.company,
            "appraisal_cycle": "Standard Cycle 2026",
            "appraisal_template": "Standard Appraisal Template",
            "custom_brief_description_of_duties": "Handling software dev tasks.",
            "custom_reporting_authority_section_a": 0,
            "custom_reporting_authority_section_b": 0,
            "custom_reporting_authority_section_c": 0,
            "custom_reviewing_authority_section_a": 0,
            "custom_reviewing_authority_section_b": 0,
            "custom_reviewing_authority_section_c": 0
        })
        appraisal.insert()
        self.assertTrue(frappe.db.exists("Appraisal", appraisal.name))
        print(f"\n[Positive Test] SUCCESS! Created ID: {appraisal.name}")

    def test_2_wrong_date_sequence_gap(self):
        """GAP CHECK: Testing invalid date sequence."""
        appraisal = frappe.get_doc({
            "doctype": "Appraisal",
            "employee": self.employee,
            "company": self.company,
            "appraisal_cycle": "Standard Cycle 2026",
            "custom_brief_description_of_duties": "Date test",
            "start_date": "2026-12-31",
            "end_date": "2026-01-01" 
        })
        try:
            appraisal.insert()
            print("\n[GAP FOUND] Appraisal allowed invalid date sequence (End < Start)!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked invalid date order.")

    def tearDown(self):
        frappe.db.rollback()