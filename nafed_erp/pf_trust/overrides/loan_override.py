import frappe

def custom_get_loan_details(doc):
    loan_details = frappe.get_all(
        "Loan",
        fields=[
            "name",
            "interest_income_account",
            "loan_account",
            "loan_product",
            "is_term_loan",
            "company"
        ],
        filters={
            "applicant": doc.employee,
            "docstatus": 1,
            "repay_from_salary": 1,
            "status": ("!=", "Closed"),
        },
    )

    return loan_details