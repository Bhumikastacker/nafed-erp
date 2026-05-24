import frappe
from frappe.tests.utils import FrappeTestCase
from frappe import ValidationError, DuplicateEntryError

class TestSalaryComponent(FrappeTestCase):

    def setUp(self):
        """
        Set up pre-requisites for Salary Component.
        """
        self.comp_name = "Basic Pay Test"
        self.abbr = "BPT"

    # ------------------------
    # Positive Test Case
    # ------------------------
    def test_1_positive_component_creation(self):
        """
        CASE 1: Verify successful creation of an Earning component.
        """
        comp = frappe.get_doc({
            "doctype": "Salary Component",
            "salary_component": self.comp_name,
            "salary_component_abbr": self.abbr,
            "type": "Earning",
            "is_tax_applicable": 1,
            "depends_on_payment_days": 1,
            "custom_is_basic_component": 1 # NAFED Custom Field
        })
        comp.insert()
        self.assertTrue(frappe.db.exists("Salary Component", self.comp_name))
        print(f"\n[Positive Test] SUCCESS! Created Component: {comp.name}")

    # ------------------------
    # Negative Test Case (Gap Check)
    # ------------------------
    def test_2_duplicate_abbr_gap(self):
        """
        GAP CHECK: Testing if system allows two components with the same Abbreviation.
        If allowed, formulas like 'BS + HRA' will break because BS is not unique.
        """
        # Pehla component
        frappe.get_doc({
            "doctype": "Salary Component",
            "salary_component": "Component One",
            "salary_component_abbr": "DUP",
            "type": "Earning"
        }).insert()

        # Doosra component wahi Abbr ke saath
        duplicate = frappe.get_doc({
            "doctype": "Salary Component",
            "salary_component": "Component Two",
            "salary_component_abbr": "DUP", # SAME ABBREVIATION
            "type": "Earning"
        })

        # Agar system do records ko same Abbr allow kar raha hai, toh ye logic GAP hai.
        try:
            duplicate.insert()
            # Check if both exist with same abbr
            if frappe.db.count("Salary Component", {"salary_component_abbr": "DUP"}) > 1:
                print("\n[GAP FOUND] Salary Component allowed DUPLICATE Abbreviations!")
        except (ValidationError, DuplicateEntryError):
            print("\n[SUCCESS] System correctly blocked duplicate Abbreviation.")

    # ------------------------
    # Logic/Default Test Case
    # ------------------------
    def test_3_default_logic_check(self):
        """
        LOGIC CHECK: Verify that 'Depends on Payment Days' is checked by default.
        (JSON mein 'default': '1' set hai)
        """
        comp = frappe.get_doc({
            "doctype": "Salary Component",
            "salary_component": "Default Logic Test",
            "salary_component_abbr": "DLT",
            "type": "Earning"
        })
        comp.insert()

        # Check default value from JSON
        self.assertEqual(comp.depends_on_payment_days, 1, "Should be enabled by default.")
        print(f"[Logic Test] SUCCESS! Default 'Depends on Payment Days' is {comp.depends_on_payment_days}")

    def tearDown(self):
        """
        Rollback changes.
        """
        frappe.db.rollback()