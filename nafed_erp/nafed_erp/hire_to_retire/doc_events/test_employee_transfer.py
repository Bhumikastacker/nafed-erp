import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import getdate, add_days, today
from frappe import ValidationError

class TestEmployeeTransfer(FrappeTestCase):

    def setUp(self):
        """
        Set up pre-requisites: Employees for 'Transfer' and 'Requested by'.
        """
        self.company = "_Test Indian Registered Company"
        
        # 1. Create a dummy Employee to be transferred
        if not frappe.db.exists("Employee", {"first_name": "TransferUser"}):
            emp = frappe.get_doc({
                "doctype": "Employee",
                "employee_number": "EMP-TRN-001",
                "first_name": "TransferUser",
                "gender": "Male",
                "date_of_joining": "2024-01-01",
                "status": "Active",
                "company": self.company,
                "date_of_birth": "1990-01-01",
                "pan_number": "ABCDE1111F",
                "custom_uan_number": "111122223333",
                "custom_vpf_applicable": "No",
                "custom_ppedate": "2024-01-01",
                "custom_allotted_official_accommodation": "No"
            })
            emp.insert()
            self.test_employee = emp.name
        else:
            self.test_employee = frappe.db.get_value("Employee", {"first_name": "TransferUser"}, "name")

        # 2. Create another employee for 'Requested by'
        if not frappe.db.exists("Employee", {"first_name": "RequesterUser"}):
            req = frappe.get_doc({
                "doctype": "Employee",
                "employee_number": "EMP-REQ-001",
                "first_name": "RequesterUser",
                "company": self.company,
                "date_of_joining": "2020-01-01"
            })
            req.insert(ignore_mandatory=True)
            self.requested_by = req.name
        else:
            self.requested_by = frappe.db.get_value("Employee", {"first_name": "RequesterUser"}, "name")

        frappe.db.commit()

    # ------------------------
    # Positive Test Case
    # ------------------------
    def test_1_positive_transfer_creation(self):
        """
        CASE 1: Verify successful creation of Employee Transfer with mandatory fields.
        """
        transfer = frappe.get_doc({
            "doctype": "Employee Transfer",
            "employee": self.test_employee,
            "transfer_date": today(),
            "custom_requested_by": self.requested_by,
            "custom_reason_for_transfer": "Promotional Transfer to Head Office",
            "company": self.company,
            
            # --- MANDATORY CHILD TABLE: transfer_details ---
            "transfer_details": [
                {
                    "property": "Department", # Using standard property for detail
                    "current": "Sales",
                    "new": "Marketing"
                }
            ]
        })
        transfer.insert()
        self.assertTrue(frappe.db.exists("Employee Transfer", transfer.name))
        print(f"\n[Positive Test] SUCCESS! Created Transfer ID: {transfer.name}")

    # ------------------------
    # Negative Test Case
    # ------------------------
    def test_2_backdated_transfer_gap(self):
        """
        GAP CHECK: Testing if system allows Transfer Date to be BEFORE the Joining Date.
        """
        # Employee joined in 2024-01-01, we try transfer in 2023
        backdate = "2023-01-01"
        transfer = frappe.get_doc({
            "doctype": "Employee Transfer",
            "employee": self.test_employee,
            "transfer_date": backdate,
            "custom_requested_by": self.requested_by,
            "custom_reason_for_transfer": "Backdated gap test",
            "transfer_details": [{"property": "Branch", "new": "Branch B"}]
        })

        try:
            transfer.insert()
            print("\n[GAP FOUND] Employee Transfer allowed BEFORE the Joining Date!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked transfer before joining.")

    # ------------------------
    # Negative Test Case
    # ------------------------
    def test_3_empty_details_gap(self):
        """
        GAP CHECK: Testing if system allows saving without any rows in Transfer Details.
        """
        transfer = frappe.get_doc({
            "doctype": "Employee Transfer",
            "employee": self.test_employee,
            "transfer_date": today(),
            "custom_requested_by": self.requested_by,
            "custom_reason_for_transfer": "Empty table test",
            "transfer_details": [] # INVALID: Empty child table
        })

        try:
            transfer.insert()
            print("[GAP FOUND] Employee Transfer allowed WITHOUT any Transfer Details!")
        except ValidationError:
            print("[SUCCESS] System correctly blocked empty transfer details.")

    def tearDown(self):
        """
        Rollback changes.
        """
        frappe.db.rollback()