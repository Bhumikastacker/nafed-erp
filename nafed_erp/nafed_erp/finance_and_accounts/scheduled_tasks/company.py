import frappe
from frappe.utils import getdate

def custom_auto_period_closing_voucher_creation():
    today = frappe.utils.nowdate()

    companies = frappe.get_all(
        "Company",
        fields=[
            "name",
            "custom_auto_period_closing_voucher_creation",
            "custom_closing_account",
            "custom_remarks"
        ]
    )

    for company in companies:
        try:
            # Run only for companies with auto PCV enabled
            if not company.custom_auto_period_closing_voucher_creation:
                continue

            fiscal_year = get_fiscal_year_record(company.name, today)
            if not fiscal_year:
                continue

            # Execute only on fiscal year end date
            if str(fiscal_year["year_end_date"]) != str(today):
                continue

            # Prevent duplicate Period Closing Voucher
            if pcv_exists(company.name, today):
                continue

            # Create PCV with fiscal year info
            create_custom_pcv(company, today, fiscal_year)

        except Exception:
            frappe.log_error(
                frappe.get_traceback(), 
                f"Custom PCV Auto Error - {company.name}"
            )



def get_fiscal_year_record(company, date):
    # Convert string date to date object so comparison works
    date = getdate(date)

    fiscal_year = frappe.db.sql(
        """
        SELECT fy.name, fy.year_start_date, fy.year_end_date
        FROM `tabFiscal Year Company` fyc
        JOIN `tabFiscal Year` fy ON fyc.parent = fy.name
        WHERE fyc.company = %s
        """,
        (company,),
        as_dict=True,
    )

    for fy in fiscal_year:
        # Now safe comparison (all are datetime.date)
        if fy.year_start_date <= date <= fy.year_end_date:
            return fy

    return None


def pcv_exists(company, posting_date):
    return frappe.db.exists(
        "Period Closing Voucher",
        {
            "company": company,
            "transaction_date": posting_date
        }
    )


def create_custom_pcv(company, posting_date, fiscal_year):
    frappe.log_error("Inside PCV", "Working")
    closing_account = company.custom_closing_account
    if not closing_account:
        return  # No closing account → no PCV

    doc = frappe.new_doc("Period Closing Voucher")
    doc.company = company.name
    doc.transaction_date = posting_date

    # 🔥 Add Fiscal Year Details
    doc.fiscal_year = fiscal_year["name"]
    doc.period_start_date = fiscal_year["year_start_date"]
    doc.period_end_date = fiscal_year["year_end_date"]

    # Closing account from Company master
    doc.closing_account_head = closing_account

    # Custom remarks
    if company.custom_remarks:
        doc.remarks = company.custom_remarks

    # Create & submit the PCV
    doc.insert(ignore_permissions=True)
    doc.submit()

    frappe.logger().info(
        f"Custom PCV created for {company.name} on {posting_date}"
    )
