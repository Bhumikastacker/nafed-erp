import frappe
from lending.loan_management.doctype.loan.loan import Loan as ERPNextLoan

class CustomLoan(ERPNextLoan):

    def validate_employee(self):
        # Get custom_is_pf_trust from Company
        is_pf_trust = frappe.get_value(
            "Company",
            self.company,
            "custom_is_pf_trust"
        )

        # If company is PF Trust → run default ERPNext validation
        if is_pf_trust:
            pass
        # Else → skip validation
        else:
            super().validate_employee()
