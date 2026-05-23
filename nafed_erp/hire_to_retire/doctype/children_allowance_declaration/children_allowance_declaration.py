# Copyright (c) 2025, CSM Technologies Pvt Ltd and contributors
# For license information, please see license.txt


import frappe
from frappe.model.document import Document
from frappe.utils import today
from frappe.utils import today, getdate



class ChildrenAllowanceDeclaration(Document):
    def validate(self):
        self.validate_date_of_application()
        self.validate_duplicate_child_names()
        self.validate_application_frequency()
        self.validate_max_two_children()
        self.calculate_allowance_amount()

    def validate_date_of_application(self):
        if self.date_of_application and self.employee:
            doj = frappe.db.get_value(
                "Employee",
                self.employee,
                "date_of_joining"
            )

            if doj and getdate(self.date_of_application) < getdate(doj):
                frappe.throw(
                    f"Date of Application ({self.date_of_application}) "
                    f"can't be before Date of Joining ({doj})."
                )

    def validate_duplicate_child_names(self):
        seen_names = set()

        for row in self.children_details:
            if not row.child_name:
                continue

            child_name = row.child_name.strip().lower()

            if child_name in seen_names:
                frappe.throw(
                    f"Child Name <b>{row.child_name}</b> is duplicated in the Children Details table."
                )

            seen_names.add(child_name)


    def validate_application_frequency(self):
        if not self.employee or not self.date_of_application:
            return

        application_date = getdate(self.date_of_application)
        year = application_date.year
        month = application_date.month

        # --------------------------------
        # 1️⃣ Only ONE application per MONTH
        # --------------------------------
        monthly_count = frappe.db.count(
            "Children Allowance Declaration",
            {
                "employee": self.employee,
                "name": ["!=", self.name],
                "docstatus": ["<", 2],
                "date_of_application": [
                    "between",
                    [f"{year}-{month:02d}-01", f"{year}-{month:02d}-31"]
                ]
            }
        )

        if monthly_count:
            frappe.throw(
                "You can create Children Allowance Declaration only once in a month."
            )

        # --------------------------------
        # 2️⃣ Maximum 12 applications per YEAR
        # --------------------------------
        yearly_count = frappe.db.count(
            "Children Allowance Declaration",
            {
                "employee": self.employee,
                "name": ["!=", self.name],
                "docstatus": ["<", 2],
                "date_of_application": [
                    "between",
                    [f"{year}-01-01", f"{year}-12-31"]
                ]
            }
        )

        if yearly_count >= 12:
            frappe.throw(
                "You can create Children Allowance Declaration only 12 times in a year."
            )
    def calculate_allowance_amount(self):
        allowance_per_child = frappe.db.get_single_value(
            "HR Settings",
            "children_allowance_amount"
        ) or 0

        valid_children_count = 0

        for row in self.children_details:
            if not row.not_applicable:
                valid_children_count += 1

        self.amount = allowance_per_child * valid_children_count

    def validate_max_two_children(self):
        if not self.children_details:
            return

        valid_children_count = 0

        for row in self.children_details:
            if not row.not_applicable:
                valid_children_count += 1

        if valid_children_count > 2:
            frappe.throw(
                "Children Allowance can be claimed for a maximum of <b>2 children</b> only."
            )


    def on_submit(self):
        self.create_additional_salary()
        self.update_employee_child_details()

    def on_update(self):
        self.update_employee_child_details()

    def create_additional_salary(self):
        # Avoid duplicate Additional Salary
        exists = frappe.db.exists(
            "Additional Salary",
            {
                "ref_doctype": "Children Allowance Declaration",
                "ref_docname": self.name
            }
        )
        if exists:
            return

        additional_salary = frappe.new_doc("Additional Salary")
        additional_salary.employee = self.employee
        additional_salary.employee_name = self.employee_name
        additional_salary.company = self.company
        additional_salary.salary_component = self.salary_component
        additional_salary.type = "Earning"
        additional_salary.currency = "INR"
        additional_salary.amount = self.amount
        additional_salary.payroll_date = self.date_of_application or today()
        additional_salary.overwrite_salary_structure_amount = 1

        # Linking
        additional_salary.ref_doctype = "Children Allowance Declaration"
        additional_salary.ref_docname = self.name

        additional_salary.insert(ignore_permissions=True)
        additional_salary.submit()

    def update_employee_child_details(self):
        if not self.employee:
            return

        employee = frappe.get_doc("Employee", self.employee)

        # Clear existing child table
        employee.custom_details = []

        # Copy rows from declaration child table
        for row in self.children_details:
            employee.append("custom_details", {
                "child_name": row.child_name,
                "date_of_birth": row.date_of_birth,
                "school_name": row.school_name,
                "class_studying_in": row.class_studying_in,
                "not_applicable": row.not_applicable
            })

        employee.save(ignore_permissions=True)






def validate(doc, method):
    if doc.date_of_application and doc.employee:
        doj = frappe.db.get_value(
            "Employee",
            doc.employee,
            "date_of_joining"
        )

        if doj and getdate(doc.date_of_application) < getdate(doj):
            frappe.throw(
                f"Date of Application ({doc.date_of_application}) "
                f"cannot be before Date of Joining ({doj})."
            )