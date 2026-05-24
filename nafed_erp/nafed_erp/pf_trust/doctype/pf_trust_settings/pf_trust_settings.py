import frappe
from frappe.model.document import Document

class PFTrustSettings(Document):

    def validate(self):
        # Header account validations
        self.validate_posting_account(
            self.employee_pf_account_for_pf_trust,
            "Employee PF Account"
        )
        self.validate_posting_account(
            self.employer_pf_account_for_pf_trust,
            "Employer PF Account"
        )
        self.validate_posting_account(
            self.voluntary_pf_account_for_pf_trust,
            "Voluntary PF Account"
        )

        # Child table validations
        self.validate_default_account_mapping()

    def validate_posting_account(self, account, label):
        if not account:
            return

        acc = frappe.get_doc("Account", account)

        # Company check
        if acc.company != self.pf_trust_company:
            frappe.throw(
                f"{label} must belong to {self.pf_trust_company}"
            )

        # Must be ledger
        if acc.is_group:
            frappe.throw(
                f"{label} must be a Ledger Account (not Group)"
            )

    def validate_default_account_mapping(self):
        seen_companies = set()

        for row in self.default_account_mapping:
            # 1️⃣ No duplicate source company
            if row.source_company in seen_companies:
                frappe.throw(
                    f"Row {row.idx}: Duplicate Source Company {row.source_company}"
                )
            seen_companies.add(row.source_company)

            if not row.default_account:
                continue

            acc = frappe.get_doc("Account", row.default_account)

            # 2️⃣ Account must belong to PF Trust Company
            if acc.company != self.pf_trust_company:
                frappe.throw(
                    f"Row {row.idx}: Account {row.default_account} must belong to {self.pf_trust_company}"
                )

            # 3️⃣ Account must be Receivable
            if acc.account_type != "Receivable":
                frappe.throw(
                    f"Row {row.idx}: Account {row.default_account} must be of type Receivable"
                )

            # 4️⃣ Must be ledger
            if acc.is_group:
                frappe.throw(
                    f"Row {row.idx}: Account {row.default_account} must be a Ledger Account"
                )

