import frappe
from hrms.payroll.doctype.payroll_entry import payroll_entry
from hrms.payroll.doctype.payroll_entry.payroll_entry import PayrollEntry
from hrms.payroll.doctype.payroll_entry.payroll_entry import set_filter_conditions


# ============================================
# 1. OVERRIDE FOR PayrollEntry.make_filters()
# ============================================

# Save original reference
_original_make_filters = PayrollEntry.make_filters

def custom_make_filters(self):
    # call original function and get base filters
    filters = _original_make_filters(self)

    # add your custom filter
    filters["employment_type"] = self.custom_employment_type

    return filters


# ============================================
# 2. OVERRIDE FOR set_filter_conditions()
# ============================================

# Save original function
_original_set_filter_conditions = set_filter_conditions

def custom_set_filter_conditions(query, filters, qb_object):
    # apply original conditions
    query = _original_set_filter_conditions(query, filters, qb_object)

    # now add your custom filter
    if filters.get("employment_type"):
        query = query.where(qb_object.employment_type == filters["employment_type"])

    return query



# In your custom app, e.g. nafed_erp/overrides/payroll_entry.py

def custom_make_journal_entry(self,
		accounts,
		currencies,
		payroll_payable_account=None,
		voucher_type="Journal Entry",
		user_remark="",
		submitted_salary_slips: list | None = None,
		submit_journal_entry=False,
		employee_wise_accounting_enabled=False,
	) -> str:

	multi_currency = 1 if len(currencies) > 1 else 0

	journal_entry = frappe.new_doc("Journal Entry")
	journal_entry.voucher_type = voucher_type
	journal_entry.user_remark = user_remark
	journal_entry.company = self.company
	journal_entry.posting_date = self.posting_date
	journal_entry.party_not_required = not employee_wise_accounting_enabled

	# 🔥 ADD YOUR FIELD HERE
	journal_entry.custom_employment_type = self.custom_employment_type

	journal_entry.set("accounts", accounts)
	journal_entry.multi_currency = multi_currency

	if voucher_type == "Journal Entry":
		journal_entry.title = payroll_payable_account

	journal_entry.save(ignore_permissions=True)

	try:
		if submit_journal_entry:
			journal_entry.submit()

		if submitted_salary_slips:
			self.set_journal_entry_in_salary_slips(
				submitted_salary_slips, jv_name=journal_entry.name
			)

	except Exception as e:
		if type(e) in (str, list, tuple):
			frappe.msgprint(e)

		self.log_error("Journal Entry creation against Salary Slip failed")
		raise

	return journal_entry.name


# Monkey-patch
PayrollEntry.make_filters= custom_make_filters
payroll_entry.set_filter_conditions = custom_set_filter_conditions
PayrollEntry.make_journal_entry = custom_make_journal_entry

