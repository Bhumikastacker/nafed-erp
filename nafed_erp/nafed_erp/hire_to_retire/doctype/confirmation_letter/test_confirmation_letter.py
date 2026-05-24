import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import getdate, add_days
from frappe import ValidationError

class TestConfirmationLetter(FrappeTestCase):

    def setUp(self):
        # 1. Setup Salutation
        if not frappe.db.exists("Salutation", "Mr."):
            frappe.get_doc({"doctype": "Salutation", "salutation": "Mr."}).insert()

        # 2. Setup Employee
        if not frappe.db.exists("Employee", {"first_name": "ConfirmUserGap"}):
            emp = frappe.get_doc({
                "doctype": "Employee",
                "employee_number": "EMP-CONF-GAP",
                "first_name": "ConfirmUserGap",
                "salutation": "Mr.",
                "gender": "Male",
                "date_of_joining": "2024-01-01", # Joining Date
                "status": "Active",
                "company": "_Test Indian Registered Company",
                "date_of_birth": "1995-01-01",
                "pan_number": "ABCDE1234Z",
                "custom_uan_number": "100200300400",
                "custom_vpf_applicable": "No",
                "custom_ppedate": "2024-06-01",
                "custom_designation_code": "MGR123",
                "custom_place_of_join": "New Delhi",
                "custom_allotted_official_accommodation": "No"
            })
            emp.insert()
            self.test_employee = emp.name
        else:
            self.test_employee = frappe.db.get_value("Employee", {"first_name": "ConfirmUserGap"}, "name")

        frappe.db.commit()

    def test_1_confirmation_letter_creation(self):
        """Positive Case: Standard confirmation letter creation"""
        confirmation = self.create_dummy_letter(self.test_employee, getdate())
        confirmation.insert()
        self.assertTrue(frappe.db.exists("Confirmation Letter", confirmation.name))
        print(f"\n[Positive Test] SUCCESS! ID: {confirmation.name}")

    def test_2_backdated_confirmation_gap(self):
        """GAP CHECK: Testing if confirmation can be BEFORE Joining Date"""
        # Employee ki joining 2024-01-01 hai, hum confirmation 2023 ki dalenge
        backdate = "2023-01-01" 
        confirmation = self.create_dummy_letter(self.test_employee, backdate)
        
        try:
            confirmation.insert()
            print("\n[GAP FOUND] Confirmation Letter allowed BEFORE Joining Date!")
        except ValidationError:
            print("\n[SUCCESS] System blocked confirmation date before joining.")

    def test_3_duplicate_letter_gap(self):
        """GAP CHECK: Testing if multiple confirmation letters allowed for same employee"""
        # Pehla letter insert karte hain
        self.create_dummy_letter(self.test_employee, getdate()).insert()
        
        # Dusra letter banane ki koshish (same employee)
        duplicate = self.create_dummy_letter(self.test_employee, getdate())
        
        try:
            duplicate.insert()
            print("[GAP FOUND] Multiple Confirmation Letters allowed for the SAME employee!")
        except ValidationError:
            print("[SUCCESS] System blocked duplicate confirmation letter.")

    def create_dummy_letter(self, employee_id, conf_date):
        """Helper to create Confirmation Letter object"""
        return frappe.get_doc({
            "doctype": "Confirmation Letter",
            "employee_id": employee_id,
            "salutation": "Mr.",
            "designation": "MGR123",
            "date_of_confirmation": conf_date,
            "place_of_posting": "New Delhi"
        })

    def tearDown(self):
        frappe.db.rollback()
# ============================================================================================================
# import frappe
# from frappe.tests.utils import FrappeTestCase
# from frappe.utils import getdate

# class TestConfirmationLetter(FrappeTestCase):

#     def setUp(self):
#         """
#         Set up pre-requisites.
#         Ensuring the Employee has all fields required for 'fetch_from' logic.
#         """
#         # 1. Create Salutation 'Mr.' if it doesn't exist
#         if not frappe.db.exists("Salutation", "Mr."):
#             frappe.get_doc({
#                 "doctype": "Salutation",
#                 "salutation": "Mr."
#             }).insert()

#         # 2. Create or Get dummy employee
#         if not frappe.db.exists("Employee", {"first_name": "ConfirmUser"}):
#             emp = frappe.get_doc({
#                 "doctype": "Employee",
#                 "employee_number": "EMP-CONF-99",
#                 "first_name": "ConfirmUser",
#                 "salutation": "Mr.",                   
#                 "gender": "Male",
#                 "date_of_joining": "2023-01-01",
#                 "status": "Active",
#                 "company": "_Test Indian Registered Company",
#                 "date_of_birth": "1995-01-01",
#                 "pan_number": "ABCDE1234Z",
#                 "custom_allotted_official_accommodation": "No",
#                 "custom_uan_number": "100200300400",
#                 "custom_vpf_applicable": 0,
#                 "custom_ppedate": "2024-01-01",        
#                 "custom_designation_code": "MGR123",   
#                 "custom_place_of_join": "New Delhi"    
#             })
#             emp.insert()
#             self.test_employee = emp.name
#         else:
#             self.test_employee = frappe.db.get_value("Employee", {"first_name": "ConfirmUser"}, "name")

#     def test_confirmation_letter_creation(self):
#         """
#         Test the creation of a Confirmation Letter.
#         """
#         confirmation = frappe.get_doc({
#             "doctype": "Confirmation Letter",
#             "employee_id": self.test_employee,
#             "salutation": "Mr.",
#             "designation": "MGR123",
#             "date_of_confirmation": getdate(),
#             "place_of_posting": "New Delhi"
#         })
        
#         # Insert the record
#         confirmation.insert()
        
#         # Commit manually for UI verification
#         # frappe.db.commit()
        
#         # Verification
#         self.assertTrue(frappe.db.exists("Confirmation Letter", confirmation.name))
#         print(f"\n[Confirmation Letter Test] SUCCESS! Created ID: {confirmation.name}")

#     def tearDown(self):
#         # Rollback changes (Commented because we used commit)
#         frappe.db.rollback()
#         # pass