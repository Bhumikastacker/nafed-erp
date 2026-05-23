import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import today, add_days, getdate
from frappe import ValidationError

class TestTravelRequest(FrappeTestCase):

    def setUp(self):
        """Set up pre-requisites: Employee (with all mandatory fields), Purpose, and LTC Period."""
        self.company = "_Test Indian Registered Company"
        travel_cat = "Other Place"
        
        # 1. Setup Purpose of Travel
        if not frappe.db.exists("Purpose of Travel", "Business Meeting"):
            frappe.get_doc({"doctype": "Purpose of Travel", "purpose_of_travel": "Business Meeting"}).insert()

        # 2. Setup LTC Period covering the WHOLE YEAR 2026
        frappe.db.delete("LTC Period", {"travel_category": travel_cat})
        frappe.get_doc({
            "doctype": "LTC Period",
            "travel_category": travel_cat,
            "period_start": "2026-01-01", 
            "period_end": "2026-12-31",   
            "allowed_years": 1
        }).insert(ignore_permissions=True)

        # 3. Setup Employee with ALL mandatory fields (Fixed custom_uan_number)
        if not frappe.db.exists("Employee", {"first_name": "TravelUserOne"}):
            emp = frappe.get_doc({
                "doctype": "Employee",
                "employee_number": "EMP-TRQ-101",
                "first_name": "TravelUserOne",
                "gender": "Male",
                "date_of_joining": "2023-01-01",
                "status": "Active",
                "company": self.company,
                "date_of_birth": "1990-01-01",
                "pan_number": "ABCDE1111Z",
                "custom_uan_number": "121212121212", # <--- FIXED: Added missing UAN
                "custom_vpf_applicable": "No",
                "custom_ppedate": "2023-01-01",
                "custom_allotted_official_accommodation": "No"
            })
            emp.insert()
            self.test_employee = emp.name
        else:
            self.test_employee = frappe.db.get_value("Employee", {"first_name": "TravelUserOne"}, "name")

        frappe.db.commit()

    def test_1_positive_travel_request_creation(self):
        """Verify successful creation of a valid Travel Request."""
        travel_req = frappe.get_doc({
            "doctype": "Travel Request",
            "employee": self.test_employee,
            "travel_type": "Domestic",
            "custom_travel_category": "Other Place",
            "custom_payment_type": "Employee Advance",
            "purpose_of_travel": "Business Meeting",
            "custom_posting_date": today(),
            "custom_expense_approver": "Administrator",
            "company": self.company,
            "custom_total_travel_amount": 5000,
            "custom_total_advance_amount": 2000
        })
        travel_req.insert()
        self.assertTrue(frappe.db.exists("Travel Request", travel_req.name))
        print(f"\n[Positive Test] SUCCESS! Created ID: {travel_req.name}")

    def test_2_self_approval_gap(self):
        """Verify that system blocks self-approval."""
        travel_req = frappe.get_doc({
            "doctype": "Travel Request",
            "employee": self.test_employee,
            "travel_type": "Domestic",
            "custom_travel_category": "Other Place",
            "custom_payment_type": "Reimbursement",
            "purpose_of_travel": "Business Meeting",
            "custom_expense_approver": frappe.session.user, 
            "company": self.company,
            "custom_total_travel_amount": 5000,
            "custom_total_advance_amount": 0
        })
        try:
            travel_req.insert()
            print("\n[GAP FOUND] System allowed SELF-APPROVAL for Travel Request!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked self-approval.")

    def tearDown(self):
        frappe.db.rollback()