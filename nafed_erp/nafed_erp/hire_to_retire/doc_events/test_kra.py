import frappe
from frappe.tests.utils import FrappeTestCase
from frappe import ValidationError

class TestKRA(FrappeTestCase):

    # ------------------------
    # Positive Test Case
    # ------------------------
    def test_1_positive_kra_creation(self):
        """
        CASE 1: Verify that a valid KRA can be created with a unique title.
        """
        kra_title = "Quality Assurance and Testing"
        
        # Cleanup if exists to ensure fresh test
        if frappe.db.exists("KRA", kra_title):
            frappe.delete_doc("KRA", kra_title)

        kra = frappe.get_doc({
            "doctype": "KRA",
            "title": kra_title, # Mandatory and Unique
            "description": "Ensuring software quality and reducing bug count."
        })
        kra.insert()
        
        # Assertion: Check if record exists in the database
        self.assertTrue(frappe.db.exists("KRA", kra_title))
        print(f"\n[Positive Test] SUCCESS! Created KRA: {kra.name}")

    # ------------------------
    # Negative Test Case
    # ------------------------
    def test_2_duplicate_title_gap(self):
        """
        GAP CHECK: Verify that the system blocks duplicate KRA titles.
        """
        duplicate_title = "Revenue Growth"
        
        # Create first record
        if not frappe.db.exists("KRA", duplicate_title):
            frappe.get_doc({"doctype": "KRA", "title": duplicate_title}).insert()

        # Attempt to create second record with SAME title
        duplicate_kra = frappe.get_doc({
            "doctype": "KRA",
            "title": duplicate_title
        })

        try:
            duplicate_kra.insert()
            print("\n[GAP FOUND] System allowed DUPLICATE KRA Titles!")
        except frappe.DuplicateEntryError:
            print("\n[SUCCESS] System correctly blocked duplicate KRA title.")

    # ------------------------
    # Negative Test Case
    # ------------------------
    def test_3_numeric_title_gap(self):
        """
        GAP CHECK: Testing if purely numeric titles are allowed for master data.
        """
        numeric_title = "123456" # INVALID DATA for a KRA
        
        if frappe.db.exists("KRA", numeric_title):
            frappe.delete_doc("KRA", numeric_title)

        kra = frappe.get_doc({
            "doctype": "KRA",
            "title": numeric_title
        })

        try:
            # We check if it saves or throws a validation error
            kra.insert()
            print("[GAP FOUND] KRA allowed a PURELY NUMERIC title!")
        except ValidationError:
            print("[SUCCESS] System blocked numeric KRA title.")

    def tearDown(self):
        """
        Rollback changes after each test.
        """
        frappe.db.rollback()