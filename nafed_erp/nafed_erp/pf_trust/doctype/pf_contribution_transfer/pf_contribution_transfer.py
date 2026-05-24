from frappe.model.document import Document
import frappe
from frappe.utils import get_first_day, get_last_day


class PFContributionTransfer(Document):
    def validate(self):
        pf_trust_company = frappe.db.get_single_value(
            "PF Trust Settings",
            "pf_trust_company"
        )

        if not pf_trust_company:
            frappe.throw("PF Trust Company is not configured in PF Trust Settings")

        if self.pf_trust_company != pf_trust_company:
            frappe.throw(
                f"PF Trust Company must be {pf_trust_company} as per PF Trust Settings"
            )

    def on_submit(self):
        self.update_salary_slips()

    def update_salary_slips(self):
        for row in self.pf_contribution:
            if not row.salary_slip:
                continue

            # Update without triggering validate/on_update of Salary Slip
            frappe.db.set_value(
                "Salary Slip",
                row.salary_slip,
                "custom_pf_contribution_transfer",
                self.name
            )




@frappe.whitelist()
def fetch_salary_slips(docname):
    doc = frappe.get_doc("PF Contribution Transfer", docname)

    if doc.docstatus != 0:
        frappe.throw("Cannot fetch after submission")

    if not doc.salary_month:
        frappe.throw("Please select Salary Month")

    # Month name → month number
    month_map = {
        "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4,
        "May": 5, "Jun": 6, "Jul": 7, "Aug": 8,
        "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
    }

    month_no = month_map.get(doc.salary_month)
    if not month_no:
        frappe.throw("Invalid Salary Month")

    # ✅ Always use current year
    year = frappe.utils.nowdate()[:4]
    year = int(year)

    # Month range
    month_start = frappe.utils.getdate(f"{year}-{month_no}-01")
    month_end = frappe.utils.get_last_day(month_start)

    # Clear existing rows
    doc.set("pf_contribution", [])

    salary_slips = frappe.get_all(
        "Salary Slip",
        filters={
            "docstatus": 1,
            "start_date": ["between", [month_start, month_end]],
            "custom_pf_contribution_transfer": ["is", "not set"]
        },
        fields=["name", "employee", "company"]
    )

    if not salary_slips:
        frappe.msgprint("No submitted Salary Slips found")
        return

    for ss in salary_slips:
        slip = frappe.get_doc("Salary Slip", ss.name)

        employee_pf = 0
        employer_pf = 0
        voluntary_pf = 0

        # Deductions
        for row in slip.deductions:
            comp_flags = frappe.db.get_value(
                "Salary Component",
                row.salary_component,
                [
                    "custom_is_employee_pf_component",
                    "custom_is_voluntary_pf_component"
                ],
                as_dict=True
            )

            if comp_flags:
                if comp_flags.custom_is_employee_pf_component:
                    employee_pf += row.amount
                if comp_flags.custom_is_voluntary_pf_component:
                    voluntary_pf += row.amount

        # Earnings
        # Employer PF = Employee PF
        employer_pf = employee_pf

        total_pf = employee_pf + employer_pf + voluntary_pf
        if total_pf <= 0:
            continue

        # Duplicate protection (current document only)
        if frappe.db.exists(
            "PF Contribution Child Table",
            {
                "parent": doc.name,
                "parenttype": "PF Contribution Transfer",
                "salary_slip": slip.name
            }
        ):
            continue

        doc.append("pf_contribution", {
            "employee_code": slip.employee,
            "source_company": slip.company,
            "salary_slip": slip.name,
            "employee_pf": employee_pf,
            "employer_pf": employer_pf,
            "voluntary_pf": voluntary_pf,
            "total_pf": total_pf
        })

    doc.save(ignore_permissions=True)
    frappe.msgprint(f"Fetched {len(doc.pf_contribution)} salary slips")


@frappe.whitelist()
def create_journal_entry(docname):
    doc = frappe.get_doc("PF Contribution Transfer", docname)

    # --------------------------------------------------
    # Basic validations
    # --------------------------------------------------
    if doc.docstatus != 1:
        frappe.throw("PF Contribution Transfer must be submitted.")

    if doc.journal_entry:
        frappe.throw("Journal Entry already created.")

    if not doc.salary_month:
        frappe.throw("Salary Month is mandatory.")

    # --------------------------------------------------
    # Load PF Trust Settings
    # --------------------------------------------------
    settings = frappe.get_single("PF Trust Settings")

    if settings.pf_trust_company != doc.pf_trust_company:
        frappe.throw("PF Trust Company mismatch with PF Trust Settings")

    # --------------------------------------------------
    # Salary month string (Select + current year)
    # --------------------------------------------------
    year = frappe.utils.now_datetime().year
    salary_month_str = f"{doc.salary_month} {year}"

    # --------------------------------------------------
    # Initialize Journal Entry
    # --------------------------------------------------
    je = frappe.new_doc("Journal Entry")
    je.voucher_type = "Journal Entry"
    je.company = doc.pf_trust_company
    je.posting_date = doc.posting_date
    je.user_remark = f"PF Consolidation for {salary_month_str}"

    # --------------------------------------------------
    # Company-wise PF Receivable breakup
    # --------------------------------------------------
    receivable_map = {}

    for row in doc.pf_contribution:
        receivable_map.setdefault(row.source_company, 0)
        receivable_map[row.source_company] += row.total_pf or 0

    # --------------------------------------------------
    # 1️⃣ Debit PF Receivable – company-wise
    # --------------------------------------------------
    for company, amount in receivable_map.items():
        if not amount:
            continue

        mapping = get_pf_receivable_mapping(settings, company)

        je.append("accounts", {
            "account": mapping.default_account,
            "party_type": "Customer",
            "party": mapping.party_name,
            "debit_in_account_currency": amount
        })

    # --------------------------------------------------
    # 2️⃣ Credit PF Payables – employee-wise
    # --------------------------------------------------
    for row in doc.pf_contribution:

        if row.employee_pf:
            je.append("accounts", {
                "account": settings.employee_pf_account_for_pf_trust,
                "party_type": "Employee",
                "party": row.employee_code,
                "credit_in_account_currency": row.employee_pf
            })

        if row.employer_pf:
            je.append("accounts", {
                "account": settings.employer_pf_account_for_pf_trust,
                "party_type": "Employee",
                "party": row.employee_code,
                "credit_in_account_currency": row.employer_pf
            })

        if row.voluntary_pf:
            je.append("accounts", {
                "account": settings.voluntary_pf_account_for_pf_trust,
                "party_type": "Employee",
                "party": row.employee_code,
                "credit_in_account_currency": row.voluntary_pf
            })

    # --------------------------------------------------
    # Save & submit
    # --------------------------------------------------
    je.custom_pf_contribution_transfer=doc.name
    je.insert()

    return je.name


def get_pf_receivable_mapping(settings, source_company):
    for row in settings.default_account_mapping:
        if row.source_company == source_company:
            return row
    frappe.throw(
        f"No PF Receivable mapping found in PF Trust Settings for company {source_company}"
    )


@frappe.whitelist()
def get_pf_trust_company():
    return frappe.db.get_single_value(
        "PF Trust Settings",
        "pf_trust_company"
    )
