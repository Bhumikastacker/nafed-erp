import frappe
from frappe.tests.utils import FrappeTestCase
from frappe import ValidationError

class TestSalaryStructure(FrappeTestCase):

    def setUp(self):
        """
        Set up pre-requisites: Company, Currency, aur Salary Components ensure karein.
        """
        self.company = "_Test Indian Registered Company"
        self.structure_name = "Standard Developer Structure"
        
        # 1. Ensure 'Basic Pay' component exists for the structure
        if not frappe.db.exists("Salary Component", "Basic Pay"):
            frappe.get_doc({
                "doctype": "Salary Component",
                "salary_component": "Basic Pay",
                "salary_component_abbr": "BP",
                "type": "Earning"
            }).insert()

        # 2. Ensure 'PF' component exists for deductions
        if not frappe.db.exists("Salary Component", "PF"):
            frappe.get_doc({
                "doctype": "Salary Component",
                "salary_component": "PF",
                "salary_component_abbr": "PF",
                "type": "Deduction"
            }).insert()

        frappe.db.commit()

    # ------------------------
    # Positive Test Case
    # ------------------------
    def test_1_positive_structure_creation(self):
        """
        CASE 1: Verify successful creation of a Salary Structure with components.
        """
        structure = frappe.get_doc({
            "doctype": "Salary Structure",
            "name": self.structure_name,
            "company": self.company,
            "currency": "INR",
            "is_active": "Yes",
            "payroll_frequency": "Monthly",
            "earnings": [
                {
                    "salary_component": "Basic Pay",
                    "amount": 50000
                }
            ],
            "deductions": [
                {
                    "salary_component": "PF",
                    "amount": 1800
                }
            ]
        })
        structure.insert()
        self.assertTrue(frappe.db.exists("Salary Structure", self.structure_name))
        print(f"\n[Positive Test] SUCCESS! Created Structure: {structure.name}")

    # ------------------------
    # Negative Test Case (Gap Check)
    # ------------------------
    def test_2_empty_components_gap(self):
        """
        GAP CHECK: Testing if system allows a Salary Structure with ZERO Earnings and Deductions.
        A structure without money components is logically useless.
        """
        structure = frappe.get_doc({
            "doctype": "Salary Structure",
            "name": "Empty Structure Test",
            "company": self.company,
            "currency": "INR",
            "is_active": "Yes",
            "earnings": [], # KHALI
            "deductions": [] # KHALI
        })

        # Agar system bina kisi component ke save karne de raha hai, toh ye ek GAP hai.
        try:
            structure.insert()
            if not structure.earnings and not structure.deductions:
                print("\n[GAP FOUND] Salary Structure allowed saving with ZERO Earnings/Deductions!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked empty salary structure.")

    # ------------------------
    # Logic Gap Check (Duplicate Check)
    # ------------------------
    def test_3_duplicate_name_gap(self):
        """
        LOGIC CHECK: Check if system allows two structures with the exact same name.
        """
        # Create first
        frappe.get_doc({
            "doctype": "Salary Structure",
            "name": "Duplicate Name Test",
            "company": self.company,
            "currency": "INR",
            "is_active": "Yes"
        }).insert()

        # Try to create second with same name
        duplicate = frappe.get_doc({
            "doctype": "Salary Structure",
            "name": "Duplicate Name Test",
            "company": self.company,
            "currency": "INR",
            "is_active": "Yes"
        })

        try:
            duplicate.insert()
            print("\n[GAP FOUND] System allowed duplicate Salary Structure names!")
        except Exception:
            print("\n[SUCCESS] System blocked duplicate structure name.")

    def tearDown(self):
        frappe.db.rollback()