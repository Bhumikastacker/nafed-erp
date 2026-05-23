import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import getdate
from frappe import ValidationError


class TestLeaveEncashment(FrappeTestCase):

    def setUp(self):

        self.company = "_Test Indian Registered Company"
        self.leave_type = "Earned Leave"
        salary_structure = "Test Encashment Structure"

        # Salary Component
        if not frappe.db.exists("Salary Component", "Basic"):
            frappe.get_doc({
                "doctype": "Salary Component",
                "salary_component": "Basic",
                "type": "Earning"
            }).insert()

        # Salary Structure
        if not frappe.db.exists("Salary Structure", salary_structure):
            frappe.get_doc({
                "doctype": "Salary Structure",
                "name": salary_structure,
                "company": self.company,
                "earnings": [
                    {"salary_component": "Basic", "amount": 50000}
                ]
            }).insert()

        # Leave Type
        if not frappe.db.exists("Leave Type", self.leave_type):
            frappe.get_doc({
                "doctype": "Leave Type",
                "leave_type_name": self.leave_type,
                "allow_encashment": 1,
                "encashment_threshold_days": 5
            }).insert()
        else:
            frappe.db.set_value("Leave Type", self.leave_type, "allow_encashment", 1)

        # Leave Period
        existing_lp = frappe.db.get_value(
            "Leave Period",
            {"company": self.company, "from_date": "2026-01-01"},
            "name"
        )

        if not existing_lp:
            lp = frappe.get_doc({
                "doctype": "Leave Period",
                "from_date": "2026-01-01",
                "to_date": "2026-12-31",
                "company": self.company
            }).insert()

            self.leave_period = lp.name
        else:
            self.leave_period = existing_lp

        # Employee
        if not frappe.db.exists("Employee", {"employee_number": "EMP-ENC-V6"}):
            emp = frappe.get_doc({
                "doctype": "Employee",
                "employee_number": "EMP-ENC-V6",
                "first_name": "EncashUserV6",
                "gender": "Male",
                "date_of_joining": "2023-01-01",
                "status": "Active",
                "company": self.company,
                "date_of_birth": "1990-01-01",
                "pan_number": "ABCDE1234F",
                "custom_uan_number": "111122223333",
                "custom_vpf_applicable": "No",
                "custom_ppedate": "2023-01-01",
                "custom_allotted_official_accommodation": "No"
            }).insert()

            self.test_employee = emp.name
        else:
            self.test_employee = frappe.db.get_value(
                "Employee",
                {"employee_number": "EMP-ENC-V6"},
                "name"
            )

        # Salary Structure Assignment
        if not frappe.db.exists(
            "Salary Structure Assignment",
            {"employee": self.test_employee, "docstatus": 1}
        ):
            assignment = frappe.get_doc({
                "doctype": "Salary Structure Assignment",
                "employee": self.test_employee,
                "salary_structure": salary_structure,
                "from_date": "2026-01-01",
                "company": self.company,
                "base": 50000
            })

            assignment.insert()
            assignment.submit()

        # Leave Allocation
        if not frappe.db.exists(
            "Leave Allocation",
            {"employee": self.test_employee, "leave_type": self.leave_type, "docstatus": 1}
        ):
            allocation = frappe.get_doc({
                "doctype": "Leave Allocation",
                "employee": self.test_employee,
                "leave_type": self.leave_type,
                "from_date": "2026-01-01",
                "to_date": "2026-12-31",
                "new_leaves_allocated": 30,
                "company": self.company
            })

            allocation.insert()
            allocation.submit()

        frappe.db.commit()

    # ------------------------------------------------------

    def test_1_positive_encashment(self):
        """CASE 1: Valid leave encashment"""

        encashment = self.create_encashment(5)

        encashment.insert()

        self.assertTrue(
            frappe.db.exists("Leave Encashment", encashment.name)
        )

        print(f"\n[Positive Test] SUCCESS! ID: {encashment.name}")

    # ------------------------------------------------------

    def test_2_threshold_validation(self):
        """
        GAP CHECK:
        Encashment below threshold (5 days)
        """

        encashment = self.create_encashment(2)

        try:
            encashment.insert()
            print("\n[GAP FOUND] System allowed encashment below threshold!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked encashment below threshold.")

    # ------------------------------------------------------

    def test_3_over_balance_encashment(self):
        """
        GAP CHECK:
        Employee has 30 leaves but tries to encash 50
        """

        encashment = self.create_encashment(50)

        try:
            encashment.insert()
            print("\n[GAP FOUND] System allowed encashment exceeding balance!")
        except ValidationError:
            print("\n[SUCCESS] System correctly blocked encashment exceeding balance.")

    # ------------------------------------------------------

    def create_encashment(self, days):

        return frappe.get_doc({
            "doctype": "Leave Encashment",
            "employee": self.test_employee,
            "leave_period": self.leave_period,
            "leave_type": self.leave_type,
            "encashment_days": days,
            "company": self.company,
            "currency": "INR",
            "encashment_date": getdate(),
            "custom_salary_component": [
                {
                    "salary_component": "Basic",
                    "amount": 5000
                }
            ]
        })

    def tearDown(self):
        frappe.db.rollback()



# ==========================================Positive Case=====================================================
# import frappe
# from frappe.tests.utils import FrappeTestCase
# from frappe.utils import getdate

# class TestLeaveEncashment(FrappeTestCase):

#     def setUp(self):
#         """
#         Set up pre-requisites: Employee, Leave Type, Allocation, 
#         and Salary Structure Assignment (Required for calculation).
#         """
#         company = "_Test Indian Registered Company"
#         leave_type_name = "Earned Leave"
        
#         # 1. Ensure Salary Component 'Basic' exists
#         if not frappe.db.exists("Salary Component", "Basic"):
#             frappe.get_doc({
#                 "doctype": "Salary Component",
#                 "salary_component": "Basic",
#                 "type": "Earning"
#             }).insert()

#         # 2. Create Salary Structure
#         salary_structure = "Test Encashment Structure"
#         if not frappe.db.exists("Salary Structure", salary_structure):
#             ss = frappe.get_doc({
#                 "doctype": "Salary Structure",
#                 "name": salary_structure,
#                 "company": company,
#                 "earnings": [{"salary_component": "Basic", "amount": 50000}]
#             }).insert()

#         # 3. Create Leave Type
#         if not frappe.db.exists("Leave Type", leave_type_name):
#             frappe.get_doc({
#                 "doctype": "Leave Type",
#                 "leave_type_name": leave_type_name,
#                 "allow_encashment": 1, 
#                 "encashment_threshold_days": 5
#             }).insert()
#         else:
#             frappe.db.set_value("Leave Type", leave_type_name, "allow_encashment", 1)

#         # 4. Create/Get Leave Period
#         existing_lp = frappe.db.get_value("Leave Period", {"company": company, "from_date": "2026-01-01"}, "name")
#         if not existing_lp:
#             lp = frappe.get_doc({
#                 "doctype": "Leave Period",
#                 "from_date": "2026-01-01",
#                 "to_date": "2026-12-31",
#                 "company": company
#             }).insert()
#             self.leave_period = lp.name
#         else:
#             self.leave_period = existing_lp

#         # 5. Create dummy Employee (V5 to be safe)
#         if not frappe.db.exists("Employee", {"first_name": "EncashUserV5"}):
#             emp = frappe.get_doc({
#                 "doctype": "Employee",
#                 "employee_number": "EMP-ENC-V5",
#                 "first_name": "EncashUserV5",
#                 "gender": "Male",
#                 "date_of_joining": "2023-01-01",
#                 "status": "Active",
#                 "company": company,
#                 "date_of_birth": "1990-01-01",
#                 "pan_number": "ABCDE1234F",
#                 "custom_uan_number": "111122223333",
#                 "custom_vpf_applicable": "No",
#                 "custom_ppedate": "2023-01-01",
#                 "custom_allotted_official_accommodation": "No"
#             })
#             emp.insert()
#             self.test_employee = emp.name
#         else:
#             self.test_employee = frappe.db.get_value("Employee", {"first_name": "EncashUserV5"}, "name")

#         # 6. ASSIGN SALARY STRUCTURE (The Fix)
#         # System needs an active assignment to calculate encashment amount
#         if not frappe.db.exists("Salary Structure Assignment", {"employee": self.test_employee, "docstatus": 1}):
#             assignment = frappe.get_doc({
#                 "doctype": "Salary Structure Assignment",
#                 "employee": self.test_employee,
#                 "salary_structure": salary_structure,
#                 "from_date": "2026-01-01",
#                 "company": company,
#                 "base": 50000
#             })
#             assignment.insert()
#             assignment.submit()

#         # 7. Create Leave Allocation (Submitted)
#         if not frappe.db.exists("Leave Allocation", {"employee": self.test_employee, "leave_type": leave_type_name, "docstatus": 1}):
#             allocation = frappe.get_doc({
#                 "doctype": "Leave Allocation",
#                 "employee": self.test_employee,
#                 "leave_type": leave_type_name,
#                 "from_date": "2026-01-01",
#                 "to_date": "2026-12-31",
#                 "new_leaves_allocated": 30,
#                 "company": company
#             })
#             allocation.insert()
#             allocation.submit()

#         self.leave_type = leave_type_name
#         frappe.db.commit()

#     def test_leave_encashment_creation(self):
#         """
#         Verify Leave Encashment creation with active salary structure.
#         """
#         encashment = frappe.get_doc({
#             "doctype": "Leave Encashment",
#             "employee": self.test_employee,
#             "leave_period": self.leave_period,
#             "leave_type": self.leave_type,
#             "encashment_days": 5,
#             "company": "_Test Indian Registered Company",
#             "currency": "INR",
#             "encashment_date": getdate(),
            
#             "custom_salary_component": [
#                 {
#                     "salary_component": "Basic",
#                     "amount": 5000
#                 }
#             ]
#         })
        
#         encashment.insert()
#         frappe.db.commit()
        
#         self.assertTrue(frappe.db.exists("Leave Encashment", encashment.name))
#         print(f"\n[Leave Encashment Test] SUCCESS! Created ID: {encashment.name}")

#     def tearDown(self):
#         pass