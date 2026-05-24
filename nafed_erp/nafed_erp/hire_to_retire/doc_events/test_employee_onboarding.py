import frappe
from frappe.tests.utils import FrappeTestCase
from frappe import ValidationError

class TestSalaryComponent(FrappeTestCase):

    def setUp(self):
        """
        Set up pre-requisites for Salary Component.
        Ensures a clean state for testing.
        """
        self.comp_name = "Basic Pay Test"
        self.abbr = "BPT"
        
        # Cleanup existing test records to avoid naming conflicts
        if frappe.db.exists("Salary Component", self.comp_name):
            frappe.delete_doc("Salary Component", self.comp_name)
            
        frappe.db.commit()

    # ------------------------
    # Positive Test Case
    # ------------------------
    def test_1_positive_component_creation(self):
        """
        Verify successful creation of a standard Earning Salary Component.
        """
        comp = frappe.get_doc({
            "doctype": "Salary Component",
            "salary_component": self.comp_name,
            "salary_component_abbr": self.abbr,
            "type": "Earning",
            "is_tax_applicable": 1,
            "depends_on_payment_days": 1,
            "custom_salary_component_type": "Salary Component"
        })
        comp.insert()
        
        self.assertTrue(frappe.db.exists("Salary Component", comp.name))
        print(f"\n[Positive Test] SUCCESS! Created Component: {comp.name}")

    # ------------------------
    # Negative Test Case (Gap Check)
    # ------------------------
    def test_2_duplicate_abbr_gap(self):
        """
        GAP CHECK: Testing if system allows two components with the same Abbreviation.
        Duplicate Abbreviations can break salary formulas (e.g., BS + HRA).
        """
        # Create first component
        self.test_1_positive_component_creation()
        
        # Try to create second component with SAME Abbreviation
        duplicate = frappe.get_doc({
            "doctype": "Salary Component",
            "salary_component": "Duplicate Abbr Test",
            "salary_component_abbr": self.abbr, # SAME AS ABOVE
            "type": "Earning"
        })

        try:
            duplicate.insert()
            print("\n[GAP FOUND] Salary Component allowed DUPLICATE Abbreviations!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked duplicate Abbreviation.")

    # ------------------------
    # Negative Test Case (Gap Check)
    # ------------------------
    def test_3_negative_percentage_gap(self):
        """
        GAP CHECK: Testing if system allows negative values in the Percentage field.
        """
        comp = frappe.get_doc({
            "doctype": "Salary Component",
            "salary_component": "Negative Percent Test",
            "salary_component_abbr": "NPT",
            "type": "Earning",
            "custom_default_percentage_": -10.5 # INVALID DATA
        })

        try:
            comp.insert()
            print("\n[GAP FOUND] Salary Component allowed NEGATIVE Percentage!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked negative percentage.")

    def tearDown(self):
        """
        Rollback changes to keep database clean.
        """
        frappe.db.rollback()