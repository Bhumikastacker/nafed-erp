import frappe 
from hrms.payroll.doctype.payroll_entry.payroll_entry import PayrollEntry as OriginalPayrollEntry

def validate_payroll_creation(doc, method):

    # Skip validation for auto-generated payroll entries
    if doc.get("custom_generated_automatically"):
        return

    # Get parent of this company
    parent_company = frappe.db.get_value("Company", doc.company, "parent_company")

    # If NO parent → this is not a child company → skip validation
    if not parent_company:
        return

    # Check if this child company requires payroll to be created from parent
    allow_from_parent = frappe.db.get_value(
        "Company",
        doc.company,
        "custom_allow_payroll_creation_from_parent_company"
    )

    # If the company requires parent-created payroll but user is trying to create manually → stop
    if allow_from_parent:
        frappe.throw(
            f"Manual Payroll Entry is not allowed for child company {doc.company}. "
            f"This payroll must be generated from the parent company {parent_company}."
        )


def automate_payroll_entry_for_all_child_companies(doc, method):
    # Check if this is parent company
    parent_company = frappe.db.get_value("Company", doc.company, "parent_company")
    if parent_company:
        return

    # Fetch child companies
    child_companies = frappe.get_all(
        "Company",
        filters={"parent_company": doc.company},
        pluck="name"
    )

    for child in child_companies:
        try:
            # Check child company setting
            allow_from_parent = frappe.db.get_value(
                "Company", child, "custom_allow_payroll_creation_from_parent_company"
            )
            if not allow_from_parent:
                continue

            # Avoid duplicates
            exists = frappe.db.exists(
                "Payroll Entry",
                {
                    "company": child,
                    "start_date": doc.start_date,
                    "end_date": doc.end_date,
                    "docstatus": 1,
                }
            )
            if exists:
                continue

            # Fetch required child data
            payroll_payable_account = frappe.db.get_value("Company", child, "default_payroll_payable_account")
            cost_center = frappe.db.get_value("Company", child, "cost_center")
            payment_account = frappe.db.get_value("Company", child, "custom_default_payment_account")

            # Check mandatory fields
            if not payroll_payable_account:
                frappe.throw(f"Child Company {child} is missing Default Payroll Payable Account.")

            if not cost_center:
                frappe.throw(f"Child Company {child} is missing Default Cost Center (custom_default_cost_center).")

            if not payment_account:
                frappe.throw(f"Child Company {child} is missing Default Payment Account (custom_default_payment_account).")

            # Create Payroll Entry
            pe = frappe.get_doc({
                "doctype": "Payroll Entry",
                "company": child,
                "start_date": doc.start_date,
                "end_date": doc.end_date,
                "posting_date": doc.posting_date,
                "payroll_frequency": doc.payroll_frequency,
                "payroll_payable_account": payroll_payable_account,
                "exchange_rate": 1,
                "cost_center": cost_center,  # 👈 ADD COST CENTER
                "payment_account": payment_account,  # 👈 ADD PAYMENT ACCOUNT
                "custom_generated_automatically": 1
            })

            pe.insert(ignore_permissions=True)

            # Fill employees
            try:
                pe.fill_employee_details()
            except Exception as fill_err:
                frappe.msgprint(
                    f"⚠ Employees could NOT be added for {child}: {str(fill_err)}"
                )

            pe.submit()

            frappe.msgprint(f"✔ Created Payroll Entry <b>{pe.name}</b> for {child}")

        except Exception as e:
            frappe.log_error(
                title=f"Payroll Auto-Create Failed for {child}",
                message=frappe.get_traceback()
            )
            frappe.msgprint(
                f"❌ Payroll for company <b>{child}</b> could not be created.<br>Error: {str(e)}"
            )



class CustomPayrollEntry(OriginalPayrollEntry):

    @frappe.whitelist()
    def submit_salary_slips(self):
        """
        Override to submit salary slips for child company payroll entries.
        No creation of salary slips, only submission.
        """

        # STEP 1: Run ERPNext's default submit logic first
        super().submit_salary_slips()

        # STEP 2: Only parent company PayrollEntry triggers child submission
        parent_company = frappe.db.get_value("Company", self.company, "parent_company")
        if parent_company:
            # This is a child company → skip
            return

        # STEP 3: Fetch child companies
        child_companies = frappe.get_all(
            "Company",
            filters={"parent_company": self.company},
            pluck="name"
        )

        for child in child_companies:

            # Find matching child payroll entry
            child_entries = frappe.get_all(
                "Payroll Entry",
                filters={
                    "company": child,
                    "payroll_frequency": self.payroll_frequency,
                    "start_date": self.start_date,
                    "end_date": self.end_date,
                },
                pluck="name"
            )

            for pe_name in child_entries:
                child_pe = frappe.get_doc("Payroll Entry", pe_name)

                # 🔥 Only submitting salary slips
                # no auto-create, just submit if available
                try:
                    super(CustomPayrollEntry, child_pe).submit_salary_slips()
                    frappe.msgprint(
                        f"✔ Salary Slips submitted for child company <b>{child}</b> "
                        f"using Payroll Entry <b>{pe_name}</b>"
                    )
                except Exception as e:
                    frappe.log_error(f"Child Salary Slip Submission Failed: {child}", str(e))
                    frappe.msgprint(
                        f"❌ Failed to submit Salary Slips for <b>{child}</b><br>Error: {str(e)}"
                    )
