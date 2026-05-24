import frappe
from frappe.model.document import Document
from frappe.utils import flt
from frappe import _
from frappe.utils import getdate

class IncrementLog(Document):

    # -----------------------------
    # BEFORE SAVE VALIDATION
    # -----------------------------
    def validate(self):
        self.validate_employee_details()
        self.validate_duplicate_increment()
        validate_increment_not_stopped(self.employee, self.increment_month, self.increment_year)
        self.validate_basic_values()

    # -----------------------------
    # ON SUBMIT → UPDATE EMPLOYEE
    # -----------------------------
    def on_submit(self):
        self.update_employee_basic()

    # -----------------------------
    # VALIDATIONS
    # -----------------------------
    def validate_duplicate_increment(self):

        exists = frappe.db.exists(
            "Increment Log",
            {
                "employee": self.employee,
                "increment_month": self.increment_month,
                "increment_year": self.increment_year,
                "docstatus": 1 
            }
        )

        # ⚠️ exclude self (important while amend)
        if exists and exists != self.name:
            frappe.throw(
                f"Increment already exists for Employee {self.employee} "
                f"for {self.increment_month} {self.increment_year}"
            )
    # -----------------------------
    # UPDATE EMPLOYEE
    # -----------------------------
    def update_employee_basic(self):

        frappe.db.set_value(
			"Employee",
			self.employee,
			"custom_basic_pay",
			str(int(self.new_basic))
		)
        
    def validate_basic_values(self):
            self.old_basic = flt(self.old_basic)
            self.new_basic = flt(self.new_basic)
            self.increment_amount = flt(self.increment_amount)
            if not self.new_basic:
                    frappe.throw("New Basic is mandatory")
            if self.new_basic <= self.old_basic:
                    frappe.throw("New Basic must be greater than Old Basic")
            if self.increment_amount <= 0:
                   frappe.throw("Increment amount must be greater than 0")

    def validate_employee_details(self):
        if self.employee:

            # 🔥 Get employee details
            emp = frappe.db.get_value(
                "Employee",
                self.employee,
                ["company", "status"],
                as_dict=True
            )

            if not emp:
                frappe.throw("Invalid Employee selected")

            # ❌ Company mismatch
            if self.company and emp.company != self.company:
                frappe.throw(
                    f"Employee <b>{self.employee}</b> does not belong to Company <b>{self.company}</b>"
                )

            # ❌ Inactive employee
            if emp.status != "Active":
                frappe.throw(
                    f"Employee <b>{self.employee}</b> is not Active"
                )

def validate_increment_not_stopped(employee, increment_month, increment_year):

    if not employee or not increment_month or not increment_year:
        return

    if frappe.db.exists(
        "Stop Increment Log",
        {
            "employee": employee,
            "increment_month": increment_month,
            "increment_year": increment_year,
            "docstatus": 1
        }
    ):
        frappe.throw(
            f"Increment is stopped for Employee {employee} for {increment_month} {increment_year}"
        )