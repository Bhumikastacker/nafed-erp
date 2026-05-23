import frappe
from frappe.tests.utils import FrappeTestCase
from frappe import ValidationError, DuplicateEntryError

class TestGrievanceType(FrappeTestCase):

    def setUp(self):
        """
        Set up pre-requisites for Grievance Type.
        """
        self.type_name = "Salary Related Issue"
        self.description = "Any grievance regarding salary, bonus, or deductions."

    # ------------------------
    # Positive Test Case
    # ------------------------
    def test_1_positive_grievance_type_creation(self):
        """
        CASE 1: Verify successful creation of a Grievance Type.
        """
        g_type = frappe.get_doc({
            "doctype": "Grievance Type",
            "name": self.type_name, # Mandatory because Naming Rule is 'Set by user'
            "description": self.description
        })
        g_type.insert()
        self.assertTrue(frappe.db.exists("Grievance Type", self.type_name))
        print(f"\n[Positive Test] SUCCESS! Created Grievance Type: {g_type.name}")

    # ------------------------
    # Negative Test Case (Gap Check)
    # ------------------------
    def test_2_duplicate_name_gap(self):
        """
        GAP CHECK: Testing if system allows two Grievance Types with the same name.
        """
        # Pehla record create karein
        frappe.get_doc({
            "doctype": "Grievance Type",
            "name": "Duplicate Test",
            "description": "First Entry"
        }).insert()

        # Doosra record wahi naam se create karne ki koshish karein
        duplicate_type = frappe.get_doc({
            "doctype": "Grievance Type",
            "name": "Duplicate Test",
            "description": "Second Entry"
        })

        # System ko DuplicateEntryError throw karna chahiye
        with self.assertRaises(DuplicateEntryError, msg="GAP FOUND: System allowed duplicate Grievance Type names!"):
            duplicate_type.insert()
        print("[SUCCESS] System correctly blocked duplicate Grievance Type name.")

    # ------------------------
    # Logic/Business Gap Check
    # ------------------------
    def test_3_empty_description_gap(self):
        """
        LOGIC GAP: System allows creating a type without any description.
        (JSON mein 'description' reqd: 0 hai, par business logic ke liye yeh gap ho sakta hai)
        """
        g_type = frappe.get_doc({
            "doctype": "Grievance Type",
            "name": "Blank Description Test",
            "description": "" # EMPTY
        })

        # Agar system save hone deta hai, toh hum ise 'GAP' ki tarah log karenge
        try:
            g_type.insert()
            if not g_type.description:
                print("\n[GAP FOUND] Grievance Type allowed saving with a BLANK description!")
        except Exception:
            print("\n[SUCCESS] System blocked empty description.")

    def tearDown(self):
        """
        Rollback database changes.
        """
        frappe.db.rollback()