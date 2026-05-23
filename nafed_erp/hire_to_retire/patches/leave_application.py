import datetime

import frappe
from frappe import _
from frappe.model.workflow import get_workflow_name
from frappe.query_builder.functions import Max, Min, Sum
from frappe.utils import (
	add_days,
	cint,
	cstr,
	date_diff,
	flt,
	formatdate,
	get_fullname,
	get_link_to_form,
	getdate,
	nowdate,
)
from hrms.hr.doctype.leave_application.leave_application import get_leave_entries, get_number_of_leave_days
import hrms.hr.doctype.leave_application.leave_application as leave_application



@frappe.whitelist()
def custom_get_leaves_for_period(
	employee: str,
	leave_type: str,
	from_date: datetime.date,
	to_date: datetime.date,
	skip_expired_leaves: bool = True,
) -> float:
	leave_entries = get_leave_entries(employee, leave_type, from_date, to_date)
	leave_days = 0
	for leave_entry in leave_entries:
		inclusive_period = leave_entry.from_date >= getdate(from_date) and leave_entry.to_date <= getdate(
			to_date
		)
		# Handle Leave Encashment (default ERPNext)
		if inclusive_period and leave_entry.transaction_type == "Leave Encashment":
			leave_days += leave_entry.leaves

		# Handle Expired Allocations
		elif (
			inclusive_period
			and leave_entry.transaction_type == "Leave Allocation"
			and leave_entry.is_expired
			and not skip_expired_leaves
		):
			leave_days += leave_entry.leaves

		# Handle Leave Application (default)
		elif leave_entry.transaction_type == "Leave Application":
			if leave_entry.from_date < getdate(from_date):
				leave_entry.from_date = from_date
			if leave_entry.to_date > getdate(to_date):
				leave_entry.to_date = to_date

			half_day = 0
			half_day_date = None
			if leave_entry.leaves % 1:
				half_day = 1
				half_day_date = frappe.db.get_value(
					"Leave Application", leave_entry.transaction_name, "half_day_date"
				)

			leave_days += (
				get_number_of_leave_days(
					employee,
					leave_type,
					leave_entry.from_date,
					leave_entry.to_date,
					half_day,
					half_day_date,
					holiday_list=leave_entry.holiday_list,
				)
				* -1
			)

		# 🔹 Handle your custom Leave Rule deductions
		elif inclusive_period and leave_entry.transaction_type == "Leave Deduction Log":
			# These are direct ledger-based deductions (not date-based applications)
			# Just apply the negative leave directly
			leave_days += leave_entry.leaves  # already negative (e.g. -1, -0.5)

	return leave_days

#Monkey Patch   
leave_application.get_leaves_for_period= custom_get_leaves_for_period