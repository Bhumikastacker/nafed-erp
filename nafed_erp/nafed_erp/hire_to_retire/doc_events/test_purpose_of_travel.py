import frappe
from frappe.tests.utils import FrappeTestCase
from frappe import ValidationError

class TestPurposeOfTravel(FrappeTestCase):

    # ------------------------
    # Positive Test Case
    # ------------------------
    def test_1_positive_purpose_creation(self):
        """
        CASE 1: Verify that a valid Purpose of Travel can be created.
        """
        purpose_name = "Client Site Visit Test"
        
        # Cleanup if exists to ensure a fresh test
        if frappe.db.exists("Purpose of Travel", purpose_name):
            frappe.delete_doc("Purpose of Travel", purpose_name)

        doc = frappe.get_doc({
            "doctype": "Purpose of Travel",
            "purpose_of_travel": purpose_name # Mandatory field for Naming
        })
        doc.insert()
        
        # Assertion: Check if record exists
        self.assertTrue(frappe.db.exists("Purpose of Travel", purpose_name))
        print(f"\n[Positive Test] SUCCESS! Created ID: {doc.name}")

    # ------------------------
    # Negative Test Case
    # ------------------------
    def test_2_numeric_name_gap(self):
        """
        GAP CHECK: Testing if purely numeric names are allowed for travel purposes.
        """
        numeric_name = "112233"
        if frappe.db.exists("Purpose of Travel", numeric_name):
            frappe.delete_doc("Purpose of Travel", numeric_name)

        doc = frappe.get_doc({
            "doctype": "Purpose of Travel",
            "purpose_of_travel": numeric_name
        })

        try:
            doc.insert()
            print("\n[GAP FOUND] Purpose of Travel allowed PURELY NUMERIC name!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked numeric master data name.")

    # ------------------------
    # Negative Test Case
    # ------------------------
    def test_3_empty_purpose_gap(self):
        """
        GAP CHECK: Testing if system allows saving without a purpose name.
        Your JSON shows 'reqd: 0', but it's used for Autoname.
        """
        doc = frappe.get_doc({
            "doctype": "Purpose of Travel",
            "purpose_of_travel": "" # INVALID: Missing ID field
        })

        try:
            doc.insert()
            print("[GAP FOUND] Purpose of Travel allowed saving without a NAME!")
        except (ValidationError, frappe.NameError):
            print("[SUCCESS] System blocked creation without a name.")

    def tearDown(self):
        """
        Rollback changes.
        """
        frappe.db.rollback()