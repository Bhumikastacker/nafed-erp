import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import today, add_days
from frappe import ValidationError

class TestVehicleLog(FrappeTestCase):

    def setUp(self):
        """
        Set up pre-requisites: UOM, Vehicle, and Employee.
        """
        self.company = "_Test Indian Registered Company"
        self.plate_no = "DL-01-AB-1234"

        # 1. Ensure UOM 'Litre' exists
        if not frappe.db.exists("UOM", "Litre"):
            frappe.get_doc({"doctype": "UOM", "uom": "Litre"}).insert()

        # 2. Create a dummy Vehicle (Fixed: Added UOM)
        if not frappe.db.exists("Vehicle", self.plate_no):
            frappe.get_doc({
                "doctype": "Vehicle",
                "license_plate": self.plate_no,
                "make": "Toyota",
                "model": "Innova",
                "last_odometer": 5000,
                "uom": "Litre" # <--- Fixed Mandatory Field
            }).insert()

        # 3. Create a dummy Employee
        if not frappe.db.exists("Employee", {"first_name": "DriverUser"}):
            emp = frappe.get_doc({
                "doctype": "Employee",
                "employee_number": "EMP-VLOG-101",
                "first_name": "DriverUser",
                "gender": "Male",
                "date_of_joining": "2020-01-01",
                "status": "Active",
                "company": self.company,
                "date_of_birth": "1990-01-01",
                "pan_number": "ABCDE1111Z",
                "custom_vpf_applicable": "No"
            })
            emp.insert(ignore_mandatory=True)
            self.test_employee = emp.name
        else:
            self.test_employee = frappe.db.get_value("Employee", {"first_name": "DriverUser"}, "name")

        frappe.db.commit()

    def test_1_positive_log_creation(self):
        """Positive Case: Standard record creation"""
        log = frappe.get_doc({
            "doctype": "Vehicle Log",
            "naming_series": "HR-VLOG-.YYYY.-",
            "license_plate": self.plate_no,
            "employee": self.test_employee,
            "date": today(),
            "odometer": 5100,
            "last_odometer": 5000
        })
        log.insert()
        self.assertTrue(frappe.db.exists("Vehicle Log", log.name))
        print(f"\n[Positive Test] SUCCESS! Created ID: {log.name}")

    def test_2_odometer_logic_gap(self):
        """GAP CHECK: Testing if Current Odometer < Last Odometer"""
        log = frappe.get_doc({
            "doctype": "Vehicle Log",
            "license_plate": self.plate_no,
            "employee": self.test_employee,
            "date": today(),
            "last_odometer": 5000,
            "odometer": 4000 # INVALID
        })
        try:
            log.insert()
            print("\n[GAP FOUND] System allowed Current Odometer < Last Odometer!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked invalid odometer.")

    def test_3_future_date_gap(self):
        """GAP CHECK: Testing if future date is allowed"""
        future_date = add_days(today(), 10)
        log = frappe.get_doc({
            "doctype": "Vehicle Log",
            "license_plate": self.plate_no,
            "employee": self.test_employee,
            "date": future_date, # INVALID
            "odometer": 5500,
            "last_odometer": 5000
        })
        try:
            log.insert()
            print("[GAP FOUND] System allowed FUTURE date for Vehicle Log!")
        except ValidationError:
            print("[SUCCESS] System blocked future date.")

    def tearDown(self):
        frappe.db.rollback()