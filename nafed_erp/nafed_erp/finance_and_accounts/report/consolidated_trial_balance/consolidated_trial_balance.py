# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

import frappe
from frappe import _
from frappe.query_builder.functions import Sum
from frappe.utils import add_days, cstr, flt, formatdate, getdate

import erpnext
from erpnext.accounts.doctype.accounting_dimension.accounting_dimension import (
    get_accounting_dimensions,
    get_dimension_with_children,
)
from erpnext.accounts.report.financial_statements import (
    filter_accounts,
    filter_out_zero_value_rows,
    set_gl_entries_by_account,
)
from erpnext.accounts.report.utils import convert_to_presentation_currency, get_currency
from erpnext.accounts.utils import get_zero_cutoff

from collections import OrderedDict, defaultdict

value_fields = (
    "opening_debit",
    "opening_credit",
    "debit",
    "credit",
    "closing_debit",
    "closing_credit",
)


# --------------------------
# Utility: Child Companies
# --------------------------
def get_child_companies(company):
    return frappe.db.get_all("Company", filters={"parent_company": company}, pluck="name")


# --------------------------
# Entry point
# --------------------------
def execute(filters=None):
    filters = frappe._dict(filters or {})
    validate_filters(filters)

    # Build the list of companies to include in the report
    companies = []

    # Always include the parent company if selected
    if filters.get("parent_company"):
        companies.append(filters.parent_company)

    # Include only the child companies explicitly selected in the report
    if filters.get("child_companies"):
        if isinstance(filters.child_companies, str):
            companies.append(filters.child_companies)
        elif isinstance(filters.child_companies, list):
            companies.extend(filters.child_companies)

    if not companies:
        frappe.throw(_("Please select at least one company"))

    filters.companies = companies

    # Fetch consolidated data and columns
    data, company_currency = get_data(filters)
    columns = get_columns(filters)

    # Optionally filter out zero rows
    if not filters.get("show_zero_values"):
        try:
            data = filter_out_zero_value_rows(data, value_fields, filters)
        except Exception:
            cutoff = get_zero_cutoff(company_currency)
            filtered = []
            for row in data:
                has_non_zero = False
                for k, v in row.items():
                    if any(k.startswith(f) for f in value_fields):
                        try:
                            if abs(flt(v)) > cutoff:
                                has_non_zero = True
                                break
                        except Exception:
                            pass
                if has_non_zero or row.get("indent") == 0:
                    filtered.append(row)
            data = filtered

    return columns, data



# --------------------------
# Filter validation
# --------------------------
def validate_filters(filters):
    if not filters.fiscal_year:
        frappe.throw(_("Fiscal Year is required"))

    fiscal_year = frappe.get_cached_value(
        "Fiscal Year", filters.fiscal_year, ["year_start_date", "year_end_date"], as_dict=True
    )

    if not fiscal_year:
        frappe.throw(_("Fiscal Year {0} does not exist").format(filters.fiscal_year))

    filters.year_start_date = getdate(fiscal_year.year_start_date)
    filters.year_end_date = getdate(fiscal_year.year_end_date)
    filters.from_date = getdate(filters.from_date or filters.year_start_date)
    filters.to_date = getdate(filters.to_date or filters.year_end_date)

    if filters.from_date > filters.to_date:
        frappe.throw(_("From Date cannot be greater than To Date"))

    if not (filters.year_start_date <= filters.from_date <= filters.year_end_date):
        frappe.msgprint(
            _("From Date should be within the Fiscal Year. Assuming From Date = {0}").format(
                formatdate(filters.year_start_date)
            )
        )
        filters.from_date = filters.year_start_date

    if not (filters.year_start_date <= filters.to_date <= filters.year_end_date):
        frappe.msgprint(
            _("To Date should be within the Fiscal Year. Assuming To Date = {0}").format(
                formatdate(filters.year_end_date)
            )
        )
        filters.to_date = filters.year_end_date


# --------------------------
# Core: Build consolidated data
# --------------------------
def get_data(filters):
    # Use the first company as master for chart of accounts
    master_company = filters.companies[0]

    # Load master company's chart of accounts (defines hierarchy)
    accounts = frappe.db.sql(
        """
        SELECT name, account_number, parent_account, account_name,
               root_type, report_type, lft, rgt
        FROM `tabAccount`
        WHERE company=%s ORDER BY lft
        """,
        master_company,
        as_dict=True,
    )

    # Build hierarchy and convenience maps
    accounts, accounts_by_name, parent_children_map = filter_accounts(accounts)
    master_map_by_account_name = {acc.account_name: acc.name for acc in accounts}

    # Prepare master data structure
    data_by_account = OrderedDict()
    for acc in accounts:
        data_by_account[acc.name] = {
            "account": acc.name,
            "parent_account": acc.parent_account,
            "indent": acc.indent,
            "account_name": acc.account_name,
        }

    # --------------------------
    # Loop through each company
    # --------------------------
    for company in filters.companies:
        company_suffix = company.lower().replace(" ", "_")
        company_filters = frappe._dict(filters)
        company_filters.company = company

        # Opening balances
        opening_balances_company = get_opening_balances(company_filters, 0)

        # GL entries grouped by account
        gl_entries_by_account = {}
        set_gl_entries_by_account(
            company,
            filters.from_date,
            filters.to_date,
            company_filters,
            gl_entries_by_account,
            root_lft=None,
            root_rgt=None,
            ignore_closing_entries=False,
            ignore_opening_entries=True,
            group_by_account=True,
        )

        # Map account full names to master account names
        remapped_gl = defaultdict(list)
        remapped_opening = {}
        acct_fulls = set(list(opening_balances_company.keys()) + list(gl_entries_by_account.keys()))
        acct_full_to_name = {}
        if acct_fulls:
            acct_rows = frappe.db.get_all(
                "Account", filters={"name": ("in", list(acct_fulls))}, fields=["name", "account_name"]
            )
            acct_full_to_name = {r.name: r.account_name for r in acct_rows}

        # Remap GL entries
        for acct_full, gl_list in gl_entries_by_account.items():
            acct_name = acct_full_to_name.get(acct_full) or frappe.db.get_value("Account", acct_full, "account_name")
            master_acc_full = master_map_by_account_name.get(acct_name)
            if master_acc_full:
                remapped_gl[master_acc_full].extend(gl_list)

        # Remap opening balances
        for acct_full, opening_row in opening_balances_company.items():
            acct_name = acct_full_to_name.get(acct_full) or frappe.db.get_value("Account", acct_full, "account_name")
            master_acc_full = master_map_by_account_name.get(acct_name)
            if master_acc_full:
                if master_acc_full not in remapped_opening:
                    remapped_opening[master_acc_full] = {"opening_debit": 0.0, "opening_credit": 0.0}
                remapped_opening[master_acc_full]["opening_debit"] += flt(opening_row.get("opening_debit", 0.0), 3)
                remapped_opening[master_acc_full]["opening_credit"] += flt(opening_row.get("opening_credit", 0.0), 3)

        # Compute final company values and merge into master data
        for master_acc in accounts:
            acc_full = master_acc.name
            gl_list = remapped_gl.get(acc_full, [])
            debit = sum(d.get("debit", 0.0) for d in gl_list)
            credit = sum(d.get("credit", 0.0) for d in gl_list)
            opening = remapped_opening.get(acc_full, {})
            opening_debit = opening.get("opening_debit", 0.0)
            opening_credit = opening.get("opening_credit", 0.0)

            closing_debit = opening_debit + debit
            closing_credit = opening_credit + credit

            row_vals = {
                "opening_debit": flt(opening_debit, 3),
                "opening_credit": flt(opening_credit, 3),
                "debit": flt(debit, 3),
                "credit": flt(credit, 3),
                "closing_debit": flt(closing_debit, 3),
                "closing_credit": flt(closing_credit, 3),
                "root_type": master_acc.get("root_type") or getattr(master_acc, "root_type", None),
            }

            if filters.get("show_net_values"):
                prepare_opening_closing(row_vals)

            # Merge into master data with company suffix
            for key in value_fields:
                data_by_account[acc_full][f"{key}_{company_suffix}"] = flt(row_vals.get(key, 0.0), 3)

    data = list(data_by_account.values())

    # Accumulate child balances into parent accounts
    data = accumulate_parent_balances(data, [f"{key}_{company.lower().replace(' ', '_')}" for key in value_fields for company in filters.companies])


    # Prepare total row
    total_row = {"account": "Total"}
    for company in filters.companies:
        suffix = company.lower().replace(" ", "_")
        for key in value_fields:
            total_row[f"{key}_{suffix}"] = sum(flt(row.get(f"{key}_{suffix}", 0.0)) for row in data)

    data.append(total_row)

    return data, frappe.get_cached_value("Company", master_company, "default_currency")



# --------------------------
# Helper: Net values
# --------------------------
def prepare_opening_closing(row):
    dr_or_cr = "debit" if row.get("root_type") in ["Asset", "Equity", "Expense"] else "credit"
    reverse_dr_or_cr = "credit" if dr_or_cr == "debit" else "debit"

    for col_type in ["opening", "closing"]:
        valid_col = f"{col_type}_{dr_or_cr}"
        reverse_col = f"{col_type}_{reverse_dr_or_cr}"

        valid_val = flt(row.get(valid_col, 0.0))
        reverse_val = flt(row.get(reverse_col, 0.0))

        net = valid_val - reverse_val
        if net < 0:
            row[reverse_col] = abs(net)
            row[valid_col] = 0.0
        else:
            row[valid_col] = net
            row[reverse_col] = 0.0


# --------------------------
# Report columns
# --------------------------
def get_columns(filters):
    columns = [
        {"label": _("Account"), "fieldname": "account", "fieldtype": "Link", "options": "Account", "width": 260}
    ]

    for company in filters.companies:
        # Get company abbreviation
        company_abbr = frappe.get_cached_value("Company", company, "abbr") or company
        suffix = company.lower().replace(" ", "_")  # Keep suffix for fieldnames

        columns.extend(
            [
                {"label": _(f"{company_abbr} Opening Debit"), "fieldname": f"opening_debit_{suffix}", "fieldtype": "Currency", "options": "currency", "width": 120},
                {"label": _(f"{company_abbr} Opening Credit"), "fieldname": f"opening_credit_{suffix}", "fieldtype": "Currency", "options": "currency", "width": 120},
                {"label": _(f"{company_abbr} Debit"), "fieldname": f"debit_{suffix}", "fieldtype": "Currency", "options": "currency", "width": 120},
                {"label": _(f"{company_abbr} Credit"), "fieldname": f"credit_{suffix}", "fieldtype": "Currency", "options": "currency", "width": 120},
                {"label": _(f"{company_abbr} Closing Debit"), "fieldname": f"closing_debit_{suffix}", "fieldtype": "Currency", "options": "currency", "width": 120},
                {"label": _(f"{company_abbr} Closing Credit"), "fieldname": f"closing_credit_{suffix}", "fieldtype": "Currency", "options": "currency", "width": 120},
            ]
        )

    return columns

# --------------------------
# Opening balances
# --------------------------
def get_opening_balances(filters, ignore_is_opening=0):
    balance_sheet_opening = get_rootwise_opening_balances(filters, "Balance Sheet", ignore_is_opening)
    pl_opening = get_rootwise_opening_balances(filters, "Profit and Loss", ignore_is_opening)
    balance_sheet_opening.update(pl_opening)
    return balance_sheet_opening


def get_rootwise_opening_balances(filters, report_type, ignore_is_opening=0):
    gle = []
    last_period_closing_voucher = ""
    ignore_closing_balances = frappe.db.get_single_value("Accounts Settings", "ignore_account_closing_balance")

    if not ignore_closing_balances:
        last_period_closing_voucher = frappe.db.get_all(
            "Period Closing Voucher",
            filters={"docstatus": 1, "company": filters.company, "period_end_date": ("<", filters.from_date)},
            fields=["period_end_date", "name"],
            order_by="period_end_date desc",
            limit=1,
        )

    accounting_dimensions = get_accounting_dimensions(as_list=False)

    if last_period_closing_voucher:
        gle = get_opening_balance(
            "Account Closing Balance",
            filters,
            report_type,
            accounting_dimensions,
            period_closing_voucher=last_period_closing_voucher[0].name,
            ignore_is_opening=ignore_is_opening,
        )
        last_date = getdate(last_period_closing_voucher[0].period_end_date)
        if last_date < getdate(add_days(filters.from_date, -1)):
            start_date = add_days(last_date, 1)
            gle += get_opening_balance(
                "GL Entry",
                filters,
                report_type,
                accounting_dimensions,
                start_date=start_date,
                ignore_is_opening=ignore_is_opening,
            )
    else:
        gle = get_opening_balance("GL Entry", filters, report_type, accounting_dimensions, ignore_is_opening=ignore_is_opening)

    opening = frappe._dict()
    for d in gle:
        opening.setdefault(d.account, {"account": d.account, "opening_debit": 0.0, "opening_credit": 0.0})
        opening[d.account]["opening_debit"] += flt(d.debit)
        opening[d.account]["opening_credit"] += flt(d.credit)
    return opening


def get_opening_balance(
    doctype,
    filters,
    report_type,
    accounting_dimensions,
    period_closing_voucher=None,
    start_date=None,
    ignore_is_opening=0,
):
    closing_balance = frappe.qb.DocType(doctype)

    accounts = frappe.db.get_all(
        "Account", filters={"company": filters.company, "report_type": report_type}, pluck="name"
    )

    opening_balance = (
        frappe.qb.from_(closing_balance)
        .select(
            closing_balance.account,
            closing_balance.account_currency,
            Sum(closing_balance.debit).as_("debit"),
            Sum(closing_balance.credit).as_("credit"),
            Sum(closing_balance.debit_in_account_currency).as_("debit_in_account_currency"),
            Sum(closing_balance.credit_in_account_currency).as_("credit_in_account_currency"),
        )
        .where((closing_balance.company == filters.company) & (closing_balance.account.isin(accounts)))
        .groupby(closing_balance.account)
    )

    if period_closing_voucher:
        opening_balance = opening_balance.where(closing_balance.period_closing_voucher == period_closing_voucher)
    else:
        if start_date:
            opening_balance = opening_balance.where(
                (closing_balance.posting_date >= start_date) & (closing_balance.posting_date < filters.from_date)
            )
            if not ignore_is_opening:
                opening_balance = opening_balance.where(closing_balance.is_opening == "No")
        else:
            if not ignore_is_opening:
                opening_balance = opening_balance.where(
                    (closing_balance.posting_date < filters.from_date) | (closing_balance.is_opening == "Yes")
                )
            else:
                opening_balance = opening_balance.where(closing_balance.posting_date < filters.from_date)

    if doctype == "GL Entry":
        opening_balance = opening_balance.where(closing_balance.is_cancelled == 0)

    if (
        not filters.show_unclosed_fy_pl_balances
        and report_type == "Profit and Loss"
        and doctype == "GL Entry"
    ):
        opening_balance = opening_balance.where(closing_balance.posting_date >= filters.year_start_date)

    if not flt(filters.with_period_closing_entry_for_opening):
        if doctype == "Account Closing Balance":
            opening_balance = opening_balance.where(closing_balance.is_period_closing_voucher_entry == 0)
        else:
            opening_balance = opening_balance.where(closing_balance.voucher_type != "Period Closing Voucher")

    if filters.cost_center:
        lft, rgt = frappe.db.get_value("Cost Center", filters.cost_center, ["lft", "rgt"])
        cost_center = frappe.qb.DocType("Cost Center")
        opening_balance = opening_balance.where(
            closing_balance.cost_center.isin(
                frappe.qb.from_(cost_center).select("name").where((cost_center.lft >= lft) & (cost_center.rgt <= rgt))
            )
        )

    if filters.project:
        opening_balance = opening_balance.where(closing_balance.project == filters.project)

    if frappe.db.count("Finance Book"):
        if filters.get("include_default_book_entries"):
            company_fb = frappe.get_cached_value("Company", filters.company, "default_finance_book")
            if filters.finance_book and company_fb and cstr(filters.finance_book) != cstr(company_fb):
                frappe.throw(_("To use a different finance book, please uncheck 'Include Default FB Entries'"))
            opening_balance = opening_balance.where(
                (closing_balance.finance_book.isin([cstr(filters.finance_book), cstr(company_fb), ""]))
                | (closing_balance.finance_book.isnull())
            )
        else:
            opening_balance = opening_balance.where(
                (closing_balance.finance_book.isin([cstr(filters.finance_book), ""]))
                | (closing_balance.finance_book.isnull())
            )

    if accounting_dimensions:
        for dimension in accounting_dimensions:
            if filters.get(dimension.fieldname):
                if frappe.get_cached_value("DocType", dimension.document_type, "is_tree"):
                    filters[dimension.fieldname] = get_dimension_with_children(
                        dimension.document_type, filters.get(dimension.fieldname)
                    )
                    opening_balance = opening_balance.where(
                        closing_balance[dimension.fieldname].isin(filters[dimension.fieldname])
                    )
                else:
                    opening_balance = opening_balance.where(
                        closing_balance[dimension.fieldname].isin(filters[dimension.fieldname])
                    )

    gle = opening_balance.run(as_dict=1)

    if filters.get("presentation_currency"):
        convert_to_presentation_currency(gle, get_currency(filters))

    return gle


def accumulate_parent_balances(data, value_fields):
    # Build mapping of account -> children
    account_map = {row["account"]: row for row in data}
    for row in reversed(data):  # Process from leaves up
        parent = row.get("parent_account")
        if parent and parent in account_map:
            parent_row = account_map[parent]
            for field in value_fields:
                parent_row[field] += row.get(field, 0.0)
    return data
