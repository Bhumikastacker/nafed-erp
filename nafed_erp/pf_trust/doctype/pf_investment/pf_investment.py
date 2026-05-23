import frappe
from frappe.model.document import Document
from frappe.utils import flt,today,getdate,add_months
from frappe.model.mapper import get_mapped_doc
from frappe import _
class PFInvestment(Document):

    def validate(self):
        self.validate_maturity_distribution()
        self.validate_investment_period_sequence()
        

    def validate_maturity_distribution(self):
        total_child_amount = 0
        total_percentage = 0

        for row in self.maturity_details_table:

            # ✅ Calculate maturity amount securely on server
            if flt(row.maturity_percentage):
                row.maturity_amount = (
                    flt(self.maturity_amount) * flt(row.maturity_percentage)
                ) / 100
            else:
                row.maturity_amount = 0

            total_child_amount += flt(row.maturity_amount)
            total_percentage += flt(row.maturity_percentage)

        # Round for financial precision safety
        total_percentage = round(total_percentage, 2)
        total_child_amount = round(total_child_amount, 2)
        parent_amount = round(flt(self.maturity_amount), 2)

        # ------------------------------------------------
        # ✅ Validation 1: Percentage should NOT exceed 100
        # ------------------------------------------------
        if total_percentage > 100:
            frappe.throw(
                f"Total Maturity Percentage ({total_percentage}%) "
                "cannot exceed 100%."
            )

        # ------------------------------------------------
        # ✅ Validation 2: If parent amount exists,
        # percentage must be exactly 100
        # ------------------------------------------------
        if parent_amount > 0 and total_percentage != 100:
            frappe.throw(
                f"Total Maturity Percentage must be 100%. "
                f"Current total is {total_percentage}%."
            )

        # ------------------------------------------------
        # ✅ Validation 3: Child amount must not exceed parent
        # ------------------------------------------------
        if total_child_amount > parent_amount:
            frappe.throw(
                f"Total Maturity Amount in Maturity Details table "
                f"({total_child_amount}) cannot exceed "
                f"Total Maturity Amount ({parent_amount})."
            )

    def validate_investment_period_sequence(self):

        if not self.maturity_details_table:
            return

        # Sort rows by idx to ensure correct order
        rows = sorted(self.maturity_details_table, key=lambda d: d.idx)

        previous_to_date = None

        for row in rows:

            if not row.investment_period_from or not row.investment_period_to:
                continue

            from_date = getdate(row.investment_period_from)
            to_date = getdate(row.investment_period_to)

            # Basic safety: from_date cannot be after to_date
            if from_date > to_date:
                frappe.throw(
                    f"Row {row.idx}: Investment Period From "
                    f"cannot be after Investment Period To."
                )

            # Check sequence with previous row
            if previous_to_date and from_date <= previous_to_date:
                frappe.throw(
                    f"Row {row.idx}: Investment Period From "
                    f"({from_date}) must be after previous row's "
                    f"Investment Period To ({previous_to_date})."
                )

            previous_to_date = to_date

@frappe.whitelist()
def make_payment_entry_from_pf_investment(source_name: str, target_doc=None):
    """
    Mapper: PF Investment -> Payment Entry
    Forces party_type = Employee and party = PF Investment.party_name
    Also maps your custom fields.
    """

    def set_missing_values(source, target):
        # Force these no matter what defaults are
        target.payment_type = "Pay"
        target.party_type = "Employee"

        # PF Investment has party_name as Link to Employee
        target.party = source.party_name

        target.company = source.company
        target.posting_date = today()

        # Link back (USE YOUR ACTUAL FIELDNAME on Payment Entry)
        # You created "custom_pf_investment" (not pf_investment)
        target.custom_pf_investment = source.name

        # Your custom amount fields
        target.custom_face_value = flt(source.face_value)
        target.custom_interest_paid = flt(source.interest_paid)
        target.custom_total_amount = flt(source.total_amount)

        # Optional: set paid_amount too if you want it prefilled
        # (Payment Entry will still need accounts/paid_from/paid_to)
        # target.paid_amount = flt(source.total_amount)

    doc = get_mapped_doc(
        "PF Investment",
        source_name,
        {
            "PF Investment": {
                "doctype": "Payment Entry",
                # no field_map needed unless names differ
            }
        },
        target_doc,
        set_missing_values
    )

    return doc

def create_payment_entry(docname: str):
    doc = frappe.get_doc("PF Investment", docname)

    if doc.docstatus != 1:
        frappe.throw(_("Payment Entry can only be created after submission."))

    # OPTIONAL: prevent duplicates
    # If you have link field in Payment Entry named "pf_investment"
    existing = frappe.db.exists("Payment Entry", {"custom_pf_investment": doc.name, "docstatus": ["!=", 2]})
    if existing:
        # Tick anyway (because it already exists) and return existing
        doc.db_set("payment_entry_created", 1)
        return existing

    pe = frappe.new_doc("Payment Entry")
    pe.payment_type = "Pay"  # or "Receive" depending on your use-case
    pe.posting_date = today()
    pe.company = doc.company

    # Link back to PF Investment (you must have this custom link field in Payment Entry)
    pe.custom_pf_investment = doc.name

    # Example party setup (adjust if your PF Investment uses Supplier/Employee/etc.)
    pe.party_type = "Supplier"
    pe.party = doc.party_name

    # Amount example (adjust to your fieldnames)
    pe.paid_amount = flt(doc.face_value) + flt(doc.interest_paid)
    pe.received_amount = 0

    pe.insert(ignore_permissions=True)

    # ✅ tick checkbox only after successful creation
    doc.db_set("payment_entry_created", 1)

    return pe.name
# @frappe.whitelist()
# def generate_interest_schedule(doc):

#     doc = frappe.parse_json(doc)

#     # run only for yearly
#     if doc.get("interest_frequency") != "Yearly":
#         return []

#     rows = []

#     face_value = flt(doc.get("face_value"))
#     rate = flt(doc.get("rate"))
#     first_interest_date = getdate(doc.get("first_interest_date"))

#     if doc.get("day_base_calculation") == "360 Days":
#         basis = 360
#     else:
#         basis = 365

#     from frappe.utils import add_months

#     interest_date = first_interest_date

#     for i in range(12):

#         next_date = add_months(interest_date, 1)

#         days = (next_date - interest_date).days

#         interest = face_value * (rate/100) * (days/basis)
#         closing = face_value + interest

#         rows.append({
#             "interest_date": interest_date,
#             "opening_face_value": face_value,
#             "interest_amount": interest,
#             "closing_value": closing,
#             "days": days
#         })

#         face_value = closing
#         interest_date = next_date

#     return rows


@frappe.whitelist()
def generate_interest_schedule(doc):

    doc = frappe.parse_json(doc)

    rows = []

    face_value = flt(doc.get("face_value"))
    rate = flt(doc.get("rate"))
    first_interest_date = getdate(doc.get("first_interest_date"))
    frequency = doc.get("interest_frequency")
    investment_category = doc.get("investment_category")
    day_base_calculation= doc.get("day_base_calculation")

    if not first_interest_date or not face_value or not rate or not frequency or not investment_category or not day_base_calculation :
        return []

    # ------------------------------------------------
    # Get Day Base from Investment Category
    # ------------------------------------------------
    basis = 365


    if investment_category:
        basis_value = day_base_calculation

        if basis_value and "360" in str(basis_value):
            basis = 360
        else:
            basis = 365

    # ------------------------------------------------
    # Frequency Map
    # ------------------------------------------------
    freq_map = {
        "Yearly": 12,
        "Half Yearly": 6,
        "Quarterly": 3,
        "Monthly": 1
    }

    months_gap = freq_map.get(frequency)

    if not months_gap:
        return []

    interest_date = first_interest_date
    periods = int(12 / months_gap)

    total_days = 0
    temp_rows = []

    # ------------------------------------------------
    # Step 1: Generate rows using actual days
    # ------------------------------------------------
    for i in range(periods):

        next_date = add_months(interest_date, months_gap)

        days = (next_date - interest_date).days

        temp_rows.append({
            "interest_date": interest_date,
            "days": days
        })

        total_days += days
        interest_date = next_date

    # ------------------------------------------------
    # Step 2: Adjust last row to match basis
    # ------------------------------------------------
    diff = total_days - basis

    if diff != 0:
        temp_rows[-1]["days"] = temp_rows[-1]["days"] - diff

    # ------------------------------------------------
    # Step 3: Calculate interest
    # ------------------------------------------------
    for row in temp_rows:

        days = row["days"]

        interest = face_value * (rate / 100) * (days / basis)

        closing = face_value + interest

        rows.append({
            "interest_date": row["interest_date"],
            "opening_face_value": face_value,
            "interest_amount": interest,
            "closing_value": closing,
            "days": days
        })

        face_value = closing

    return rows

@frappe.whitelist()
def create_all_journal_entries(docname):

    doc = frappe.get_doc("PF Investment", docname)

    # -----------------------------------------
    # Basic Validation
    # -----------------------------------------
    if doc.docstatus != 1:
        frappe.throw("PF Investment must be submitted.")

    # -----------------------------------------
    # Helper Function (IMPORTANT)
    # -----------------------------------------
    def validate_account(acc, label):
        if not acc:
            frappe.throw(f"{label} is not set properly. Please configure it.")
        return acc

    # =========================================
    # 1️⃣ MAIN JOURNAL ENTRY
    # =========================================
    existing_main = frappe.db.exists(
        "Journal Entry",
        {
            "custom_pf_investment": doc.name,
            "custom_jv_type": "Main",
            "docstatus": 1
        }
    )

    if existing_main:
        frappe.throw(f"Main Journal Entry already exists: {existing_main}")

    # Investment Account
    investment_account = frappe.db.get_value(
        "Investment Category", doc.investment_category, "investment_account"
    )
    investment_account = validate_account(investment_account, "Investment Account")

    # Supplier Payable Account
    supplier = frappe.get_doc("Supplier", doc.party_name)

    payable_account = None
    for row in supplier.accounts:
        if row.company == doc.company:
            payable_account = row.account
            break

    payable_account = validate_account(payable_account, "Supplier Payable Account")

    # Interest Paid Account
    interest_paid_account = frappe.db.get_value(
        "Investment Category",
        doc.investment_category,
        "accrued_interest_paid_account"
    )

    if flt(doc.interest_paid) > 0:
        interest_paid_account = validate_account(
            interest_paid_account,
            "Accrued Interest Paid Account"
        )

    # -----------------------------------------
    # Create Main JE
    # -----------------------------------------
    je = frappe.new_doc("Journal Entry")
    je.voucher_type = "Journal Entry"
    je.posting_date = today()
    je.company = doc.company
    je.custom_pf_investment = doc.name
    je.custom_jv_type = "Main"
    je.user_remark = f"Journal Entry for PF Investment {doc.name}"

    total_credit = flt(doc.face_value)

    # Debit → Investment
    je.append("accounts", {
        "account": investment_account,
        "debit_in_account_currency": flt(doc.face_value)
    })

    # Debit → Interest Paid
    if flt(doc.interest_paid) > 0:
        je.append("accounts", {
            "account": interest_paid_account,
            "debit_in_account_currency": flt(doc.interest_paid)
        })
        total_credit += flt(doc.interest_paid)

    # Credit → Supplier
    je.append("accounts", {
        "account": payable_account,
        "party_type": "Supplier",
        "party": doc.party_name,
        "credit_in_account_currency": total_credit
    })

    # 🔍 Safety Check (VERY IMPORTANT)
    for acc in je.accounts:
        if not acc.account:
            frappe.throw(f"Missing account in Main JE row: {acc}")

    je.insert(ignore_permissions=True)

    # =========================================
    # 2️⃣ INTEREST ACCRUAL JVs
    # =========================================

    created_jvs = []

    if doc.table_hrug:

        category = frappe.get_doc("Investment Category", doc.investment_category)

        debit_account = validate_account(
            category.interest_recievable_account,
            "Interest Receivable Account"
        )

        credit_account = validate_account(
            category.return_on_investment_account,
            "Return on Investment Account"
        )

        for row in doc.table_hrug:

            if not row.interest_amount:
                continue

            # 🚫 Skip if already created
            if row.journal_entry:
                continue

            accrual_je = frappe.new_doc("Journal Entry")
            accrual_je.voucher_type = "Journal Entry"
            accrual_je.company = doc.company
            accrual_je.posting_date = row.interest_date
            accrual_je.custom_pf_investment = doc.name
            accrual_je.custom_jv_type = "Interest"
            accrual_je.user_remark = f"Interest Accrual for PF Investment {doc.name}"

            accrual_je.append("accounts", {
                "account": debit_account,
                "debit_in_account_currency": flt(row.interest_amount)
            })

            accrual_je.append("accounts", {
                "account": credit_account,
                "credit_in_account_currency": flt(row.interest_amount)
            })

            accrual_je.insert(ignore_permissions=True)

            # ✅ Store reference in row
            row.db_set("journal_entry", accrual_je.name)

            created_jvs.append(accrual_je.name)

    # =========================================
    # FINAL RESPONSE
    # =========================================
    return {
        "main_jv": je.name,
        "interest_jvs": created_jvs
    }