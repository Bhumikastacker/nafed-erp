import frappe
from frappe.utils import flt, getdate, today


def validate(doc, method):
    validate_loan_application(doc)


def validate_loan_application(doc):

    if not doc.loan_product:
        return

    loan_product = frappe.get_doc("Loan Product", doc.loan_product)

    if not loan_product.custom_loan_type:
        return

    loan_type = frappe.get_doc("Loan Type", loan_product.custom_loan_type)

    if not loan_type.advance_category:
        return

    # Route based on Advance Category
    if loan_type.advance_category == "Housing Related Advance (Para 68B)":
        validate_para_68b(doc, loan_type)

    elif loan_type.advance_category == "Withdrawal For Repayment of Loans (Para 68BB)":
        validate_para_68bb(doc, loan_type)

    elif loan_type.advance_category == "Unemployment Advance (Para 68H)":
        validate_para_68h(doc, loan_type)

    elif loan_type.advance_category == "Medical Advance (Para 68J)":
        validate_para_68j(doc, loan_type)

    elif loan_type.advance_category == "Marriage/Education Advance (Para 68K)":
        validate_para_68k(doc, loan_type)

    elif loan_type.advance_category == "Physical Disability Advance (Para 68N)":
        validate_para_68n(doc, loan_type)

    elif loan_type.advance_category == "Pre Retirement Advance (Para 68NN)":
        validate_para_68nn(doc, loan_type)

def validate_para_68b(doc, loan_type):

    validate_membership_from_loan_type(doc,loan_type)

    eligible_amounts = []

    # ---------------------------------------------------
    # 1️⃣ Salary Month Limit (if enabled)
    # ---------------------------------------------------
    if loan_type.use_salary_month_limit:

        salary_months_limit = None

        # If sub-category rules exist
        if loan_type.housing_rules:

            if not doc.custom_housing_sub_category:
                frappe.throw("Please select Housing Sub Category.")

            for row in loan_type.housing_rules:
                if row.sub_category == doc.custom_housing_sub_category:
                    salary_months_limit = flt(row.salary_months_limit)
                    break

            if not salary_months_limit:
                frappe.throw("Salary Months Limit not configured for selected sub category.")


        wage_limit = get_salary_total_for_last_n_months(
            doc.applicant,
            int(salary_months_limit)
        )

        eligible_amounts.append(wage_limit)

    # ---------------------------------------------------
    # 2️⃣ Total Share Rule
    # ---------------------------------------------------
    if loan_type.use_total_employee_and_employer_share_with_interest:

        total_share = calculate_total_employee_employer_share(doc)
        eligible_amounts.append(total_share)


    # ---------------------------------------------------
    # 3️⃣ Employee Share Only Rule
    # ---------------------------------------------------
    if loan_type.use_employee_share_with_interest_only:

        employee_share = calculate_employee_share_with_interest(doc)
        eligible_amounts.append(employee_share)

    # ---------------------------------------------------
    # 4️⃣ Apply Total Cost Cap (Mandatory in Housing)
    # ---------------------------------------------------
    if doc.custom_total_cost:
        eligible_amounts.append(flt(doc.custom_total_cost))

    # ---------------------------------------------------
    # Final Eligible
    # ---------------------------------------------------
    if not eligible_amounts:
        frappe.throw("No admissible condition configured for this Loan Type.")

    final_eligible_amount = min(eligible_amounts)

    doc.custom_eligible_amount = final_eligible_amount

    if flt(doc.loan_amount) > final_eligible_amount:
        frappe.throw(
            f"Maximum eligible amount under Para 68B is {final_eligible_amount}"
        )


def validate_para_68bb(doc, loan_type):

    validate_membership_from_loan_type(doc,loan_type)

    eligible_amounts = []

    # ---------------------------------------------------
    # 1️⃣ Salary Month Limit Rule
    # ---------------------------------------------------
    if loan_type.use_salary_month_limit:

        salary_months_limit = flt(loan_type.salary_months_limit)

        if not salary_months_limit:
            frappe.throw("Salary Months Limit not configured in Loan Type.")

        wage_limit = get_salary_total_for_last_n_months(
            doc.applicant,
            int(salary_months_limit)
        )

        eligible_amounts.append(wage_limit)

    # ---------------------------------------------------
    # 2️⃣ Total Employee + Employer Share Rule
    # ---------------------------------------------------
    if loan_type.use_total_employee_and_employer_share_with_interest:

        total_share = calculate_total_employee_employer_share(doc)
        eligible_amounts.append(total_share)

    if doc.custom_total_cost:
        eligible_amounts.append(flt(doc.custom_total_cost))
    # ---------------------------------------------------
    # Final Eligible Amount
    # ---------------------------------------------------
    if not eligible_amounts:
        frappe.throw("No admissible condition configured for Para 68BB.")

    final_eligible_amount = min(eligible_amounts)

    doc.custom_eligible_amount = final_eligible_amount

    if flt(doc.loan_amount) > final_eligible_amount:
        frappe.throw(
            f"Maximum eligible amount under Para 68BB is {final_eligible_amount}"
        )

def validate_para_68h(doc, loan_type):

    validate_membership_from_loan_type(doc,loan_type)

    # ---------------------------------------------------
    # 1️⃣ Employee Share With Interest Only
    # ---------------------------------------------------
    if loan_type.use_employee_share_with_interest_only:

        eligible_amount = calculate_employee_share_with_interest(doc)

        if eligible_amount <= 0:
            frappe.throw("No employee PF balance available.")

    # ---------------------------------------------------
    # 2️⃣ Share Percentage Limit
    # ---------------------------------------------------
    elif loan_type.use_share_percentage_limit:

        if not loan_type.share_percentage_on:
            frappe.throw("Share Percentage On is not configured in Loan Type.")

        if not loan_type.share_percentage_value:
            frappe.throw("Share Percentage Value is not configured in Loan Type.")

        base_amount = 0

        if loan_type.share_percentage_on == "Employee Share":
            base_amount = calculate_employee_share_with_interest(doc)

        elif loan_type.share_percentage_on == "Employer Share":
            base_amount = calculate_employer_share_with_interest(doc)

        if base_amount <= 0:
            frappe.throw("No PF balance available for percentage calculation.")

        eligible_amount = base_amount * (
            flt(loan_type.share_percentage_value) / 100
        )

    else:
        frappe.throw("No admissible condition configured for Para 68H.")

    # ---------------------------------------------------
    # Final Validation
    # ---------------------------------------------------
    doc.custom_eligible_amount = eligible_amount

    if flt(doc.loan_amount) > eligible_amount:
        frappe.throw(
            f"Maximum eligible amount under Para 68H is {eligible_amount}"
        )

def validate_para_68j(doc, loan_type):

    validate_membership_from_loan_type(doc,loan_type)

    eligible_amounts = []

    # ---------------------------------------------------
    # 1️⃣ Salary Month Limit Rule
    # ---------------------------------------------------
    if loan_type.use_salary_month_limit:

        salary_months_limit = flt(loan_type.salary_months_limit)

        if not salary_months_limit:
            frappe.throw("Salary Months Limit not configured in Loan Type.")

        wage_limit = get_salary_total_for_last_n_months(
            doc.applicant,
            int(salary_months_limit)
        )

        eligible_amounts.append(wage_limit)

    # ---------------------------------------------------
    # 2️⃣ Employee Share With Interest Only
    # ---------------------------------------------------
    if loan_type.use_employee_share_with_interest_only:

        employee_share = calculate_employee_share_with_interest(doc)

        if employee_share <= 0:
            frappe.throw("No employee PF balance available.")

        eligible_amounts.append(employee_share)

    # ---------------------------------------------------
    # Final Validation
    # ---------------------------------------------------
    if not eligible_amounts:
        frappe.throw("No admissible condition configured for Para 68J.")

    final_eligible_amount = min(eligible_amounts)

    doc.custom_eligible_amount = final_eligible_amount

    if flt(doc.loan_amount) > final_eligible_amount:
        frappe.throw(
            f"Maximum eligible amount under Para 68J is {final_eligible_amount}"
        )

def validate_para_68k(doc, loan_type):

    validate_membership_from_loan_type(doc,loan_type)

    # ---------------------------------------------------
    # Only Share Percentage Rule Allowed
    # ---------------------------------------------------
    if not loan_type.use_share_percentage_limit:
        frappe.throw("Share Percentage Limit must be enabled for Para 68K.")

    if loan_type.share_percentage_on != "Employee Share":
        frappe.throw("Para 68K allows percentage only on Employee Share.")

    if not loan_type.share_percentage_value:
        frappe.throw("Share Percentage Value not configured in Loan Type.")

    # Get Employee Share Balance
    employee_share = calculate_employee_share_with_interest(doc)

    if employee_share <= 0:
        frappe.throw("No employee PF balance available.")

    # Calculate Percentage Limit
    eligible_amount = employee_share * (
        flt(loan_type.share_percentage_value) / 100
    )

    # ---------------------------------------------------
    # Final Validation
    # ---------------------------------------------------
    doc.custom_eligible_amount = eligible_amount

    if flt(doc.loan_amount) > eligible_amount:
        frappe.throw(
            f"Maximum eligible amount under Para 68K is {eligible_amount}"
        )

def validate_para_68n(doc, loan_type):

    validate_membership_from_loan_type(doc,loan_type)

    eligible_amounts = []

    # ---------------------------------------------------
    # Rule 1 → Salary Month Limit
    # ---------------------------------------------------
    if loan_type.use_salary_month_limit:

        salary_months_limit = flt(loan_type.salary_months_limit)

        if not salary_months_limit:
            frappe.throw("Salary Months Limit not configured in Loan Type.")

        wage_limit = get_salary_total_for_last_n_months(
            doc.applicant,
            int(salary_months_limit)
        )

        eligible_amounts.append(flt(wage_limit))

    # ---------------------------------------------------
    # Rule 2 → Employee Share With Interest Only
    # ---------------------------------------------------
    if loan_type.use_employee_share_with_interest_only:

        employee_share = calculate_employee_share_with_interest(doc)

        if employee_share <= 0:
            frappe.throw("No employee PF balance available.")

        eligible_amounts.append(flt(employee_share))

    # ---------------------------------------------------
    # Rule 3 → Total Cost (Mandatory Upper Cap)
    # ---------------------------------------------------
    if not doc.custom_total_cost:
        frappe.throw("Total Cost is required for Para 68N.")

    eligible_amounts.append(flt(doc.custom_total_cost))


    # ---------------------------------------------------
    # Find Least Eligible Amount
    # ---------------------------------------------------
    final_eligible_amount = min(eligible_amounts)

    # ---------------------------------------------------
    # Set Values
    # ---------------------------------------------------
    doc.custom_eligible_amount = final_eligible_amount


    # ---------------------------------------------------
    # Final Validation (Safety)
    # ---------------------------------------------------
    if flt(doc.loan_amount) > final_eligible_amount:
        frappe.throw(
            f"Maximum eligible amount under Para 68N is {final_eligible_amount}"
        )

def validate_para_68nn(doc, loan_type):

    validate_membership_from_loan_type(doc,loan_type)
    
    # ---------------------------------------------------
    # Validate Configuration
    # ---------------------------------------------------
    if not loan_type.use_share_percentage_limit:
        frappe.throw("Share Percentage Limit must be enabled for Para 68NN.")

    if loan_type.share_percentage_on != "Total":
        frappe.throw("Para 68NN allows percentage only on Total balance.")

    if not loan_type.share_percentage_value:
        frappe.throw("Share Percentage Value not configured in Loan Type.")

    # ---------------------------------------------------
    # Get Total PF Balance (Employee + Employer + Interest)
    # ---------------------------------------------------
    total_balance = calculate_total_employee_employer_share(doc)

    if total_balance <= 0:
        frappe.throw("No PF balance available.")

    # ---------------------------------------------------
    # Calculate Eligible Amount
    # ---------------------------------------------------
    eligible_amount = total_balance * (
        flt(loan_type.share_percentage_value) / 100
    )

    doc.custom_eligible_amount = eligible_amount

    # ---------------------------------------------------
    # Final Validation
    # ---------------------------------------------------
    if flt(doc.loan_amount) > eligible_amount:
        frappe.throw(
            f"Maximum eligible amount under Para 68NN is {eligible_amount}"
        )

def get_pf_trust_accounts(company):

    settings = frappe.get_single("PF Trust Settings")

    if settings.pf_trust_company != company:
        frappe.throw("PF Trust Company mismatch in PF Trust Settings.")

    return {
        "employee_account": settings.employee_pf_account_for_pf_trust,
        "employer_account": settings.employer_pf_account_for_pf_trust,
        "voluntary_account": settings.voluntary_pf_account_for_pf_trust
    }

def get_account_balance(account, party=None):

    filters = {
        "account": account,
        "is_cancelled": 0
    }

    if party:
        filters["party"] = party

    balance = frappe.db.sql("""
        SELECT COALESCE(SUM(debit - credit), 0)
        FROM `tabGL Entry`
        WHERE account = %(account)s
        AND is_cancelled = 0
        {party_condition}
    """.format(
        party_condition="AND party = %(party)s" if party else ""
    ), filters)[0][0]

    return abs(flt(balance))


def calculate_employee_share_with_interest(doc):

    accounts = get_pf_trust_accounts(doc.company)

    employee_balance = get_account_balance(
        accounts["employee_account"],
        party=doc.applicant
    )

    voluntary_balance = get_account_balance(
        accounts["voluntary_account"],
        party=doc.applicant
    )

    total_employee_share = employee_balance + voluntary_balance

    return total_employee_share

def calculate_employer_share_with_interest(doc):

    accounts = get_pf_trust_accounts(doc.company)

    employer_balance = get_account_balance(
        accounts["employer_account"],
        party=doc.applicant
    )

    return employer_balance


def calculate_total_employee_employer_share(doc):

    employee_share = calculate_employee_share_with_interest(doc)
    employer_share = calculate_employer_share_with_interest(doc)

    return employee_share + employer_share


def get_salary_total_for_last_n_months(employee, months):

    salary_slips = frappe.get_all(
        "Salary Slip",
        filters={
            "employee": employee,
            "docstatus": 1
        },
        fields=["name"],
        order_by="end_date desc",
        limit=months
    )

    if not salary_slips:
        return 0

    slip_names = [d.name for d in salary_slips]

    earnings = frappe.get_all(
        "Salary Detail",
        filters={
            "parent": ["in", slip_names],
            "parentfield": "earnings"
        },
        fields=["salary_component", "amount"]
    )

    components = frappe.get_all(
        "Salary Component",
        filters={
            "name": ["in", list(set([e.salary_component for e in earnings]))]
        },
        fields=[
            "name",
            "custom_is_basic_component",
            "custom_is_da_component"
        ]
    )

    component_map = {
        c.name: c for c in components
    }

    total = 0

    for e in earnings:
        comp = component_map.get(e.salary_component)
        if comp and (comp.custom_is_basic_component or comp.custom_is_da_component):
            total += flt(e.amount)

    return total


def validate_membership_from_loan_type(doc, loan_type):

    if not loan_type.membership_period:
        return

    if not doc.applicant:
        frappe.throw("Employee is required.")

    # Fetch Employee Date of Joining
    date_of_joining = frappe.db.get_value(
        "Employee",
        doc.applicant,
        "date_of_joining"
    )

    if not date_of_joining:
        frappe.throw("Date of Joining is not set in Employee master.")

    days_completed = (getdate(today()) - getdate(date_of_joining)).days

    # Convert required membership to days
    if loan_type.membership_period_type == "Years":
        required_days = loan_type.membership_period * 365
    else:
        required_days = loan_type.membership_period * 30

    if days_completed < required_days:
        frappe.throw(
            f"Minimum {loan_type.membership_period} "
            f"{loan_type.membership_period_type} membership required."
        )

