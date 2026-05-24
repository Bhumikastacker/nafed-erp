import frappe
from frappe.tests.utils import FrappeTestCase
from frappe import ValidationError

class TestVehicleServiceItem(FrappeTestCase):

    # ------------------------
    # Positive Test Case
    # ------------------------
    def test_1_positive_service_item_creation(self):
        """
        Verify that a valid Vehicle Service Item can be created.
        """
        item_name = "Oil Filter Change Test"
        
        # Cleanup if exists to ensure a fresh test
        if frappe.db.exists("Vehicle Service Item", item_name):
            frappe.delete_doc("Vehicle Service Item", item_name)

        service_item = frappe.get_doc({
            "doctype": "Vehicle Service Item",
            "service_item": item_name # Mandatory field (acts as ID)
        })
        service_item.insert()
        
        # Assertion: Check if record exists in database
        self.assertTrue(frappe.db.exists("Vehicle Service Item", item_name))
        print(f"\n[Positive Test] SUCCESS! Created ID: {service_item.name}")

    # ------------------------
    # Negative Test Case
    # ------------------------
    def test_2_duplicate_name_gap(self):
        """
        GAP CHECK: Verify that duplicate service item names are blocked.
        """
        duplicate_name = "Brake Inspection"
        
        # Create first record
        if not frappe.db.exists("Vehicle Service Item", duplicate_name):
            frappe.get_doc({
                "doctype": "Vehicle Service Item",
                "service_item": duplicate_name
            }).insert()

        # Attempt to create second record with SAME name
        duplicate = frappe.get_doc({
            "doctype": "Vehicle Service Item",
            "service_item": duplicate_name
        })

        try:
            duplicate.insert()
            print("\n[GAP FOUND] System allowed DUPLICATE Vehicle Service Items!")
        except frappe.DuplicateEntryError:
            print("\n[SUCCESS] System correctly blocked duplicate service item names.")

    # ------------------------
    # Negative Test Case
    # ------------------------
    def test_3_numeric_name_gap(self):
        """
        GAP CHECK: Testing if purely numeric names are allowed for master data.
        """
        numeric_name = "887766"
        if frappe.db.exists("Vehicle Service Item", numeric_name):
            frappe.delete_doc("Vehicle Service Item", numeric_name)

        service_item = frappe.get_doc({
            "doctype": "Vehicle Service Item",
            "service_item": numeric_name
        })

        try:
            service_item.insert()
            print("[GAP FOUND] Vehicle Service Item allowed a PURELY NUMERIC name!")
        except ValidationError:
            print("[SUCCESS] System blocked numeric master data name.")

    def tearDown(self):
        """
        Rollback changes to keep the database clean.
        """
        frappe.db.rollback()