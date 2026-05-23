import frappe

@frappe.whitelist()
def create_additional_salaries(expense_claim):
    """Create missing Additional Salary entries for the Expense Claim."""

    ec = frappe.get_doc("Expense Claim", expense_claim)

    if ec.docstatus != 1:
        frappe.throw("Submit the Expense Claim before creating Additional Salaries.")

    if not ec.expenses:
        frappe.throw("No expense rows found in this Expense Claim.")

    count = 0

    for row in ec.expenses:

        if not row.expense_type:
            continue

        # Salary Component
        salary_component = frappe.db.get_value(
            "Expense Claim Type",
            row.expense_type,
            "custom_salary_component"
        )

        if not salary_component:
            frappe.throw(
                f"No Salary Component set in Expense Claim Type: <b>{row.expense_type}</b>"
            )

        # CHECK IF ADDITIONAL SALARY ALREADY EXISTS FOR THIS ROW
        existing = frappe.db.exists(
            "Additional Salary",
            {
                "ref_doctype": "Expense Claim",
                "ref_docname": ec.name,
                "salary_component": salary_component,
                "amount": row.amount,
                "employee": ec.employee,
                "docstatus": 1  # submitted only
            }
        )

        if existing:
            # Already created — skip
            continue

        # Create missing Additional Salary
        add_sal = frappe.new_doc("Additional Salary")
        add_sal.employee = ec.employee
        add_sal.company = ec.company
        add_sal.salary_component = salary_component
        add_sal.amount = row.amount
        add_sal.ref_doctype = "Expense Claim"
        add_sal.ref_docname = ec.name
        add_sal.payroll_date = frappe.utils.today()
        add_sal.insert(ignore_permissions=True)
        add_sal.submit()

        count += 1

    return f"{count} missing Additional Salary records created."



@frappe.whitelist()
def additional_salaries_status(expense_claim):
    """Check if all required additional salaries are created."""

    ec = frappe.get_doc("Expense Claim", expense_claim)

    total_expenses = len(ec.expenses)

    created = frappe.db.count(
        "Additional Salary",
        {
            "ref_doctype": "Expense Claim",
            "ref_docname": expense_claim,
            "docstatus": 1
        }
    )

    return {
        "total_expenses": total_expenses,
        "created": created,
        "all_created": created == total_expenses
    }


def set_expense_claim_reference_in_travel_request(doc, method):
    if not doc.custom_travel_request_:
        return

    existing = frappe.db.get_value(
        "Travel Request",
        doc.custom_travel_request_,
        "custom_expense_claim"
    )

    if not existing:
        frappe.db.set_value(
            "Travel Request",
            doc.custom_travel_request_,
            "custom_expense_claim",
            doc.name
        )


def remove_expense_claim_reference_in_travel_request(doc, method):
    if doc.custom_travel_request_:
        frappe.db.set_value(
            "Travel Request",
            doc.custom_travel_request_,
            "custom_expense_claim",
            None
        )