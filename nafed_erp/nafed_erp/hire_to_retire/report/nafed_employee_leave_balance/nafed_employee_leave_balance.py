# Copyright (c) 2013, Frappe Technologies Pvt. Ltd.
# For license information, please see license.txt

from itertools import groupby

import frappe
from frappe import _
from frappe.query_builder.functions import Abs, Sum
from frappe.utils import add_days, cint, flt, getdate

from hrms.hr.doctype.leave_allocation.leave_allocation import get_previous_allocation
from hrms.hr.doctype.leave_application.leave_application import (
	get_leave_balance_on,
	get_leaves_for_period,
)

Filters = frappe._dict


def execute(filters=None):
	filters = frappe._dict(filters or {})

	from_date = filters.get("from_date")
	to_date = filters.get("to_date")

	if not from_date or not to_date:
		frappe.throw(_("Please set both From Date and To Date"))

	if to_date <= from_date:
		frappe.throw(_('"From Date" cannot be greater than or equal to "To Date"'))

	columns = get_columns()
	data = get_data(filters)
	charts = get_chart_data(data, filters)
	return columns, data, None, charts


def get_columns():
	return [
		{"label": _("Leave Type"), "fieldtype": "Link", "fieldname": "leave_type", "width": 180, "options": "Leave Type"},
		{"label": _("Employee"), "fieldtype": "Link", "fieldname": "employee", "width": 120, "options": "Employee"},
		{"label": _("Employee Name"), "fieldtype": "Data", "fieldname": "employee_name", "width": 160},
		{"label": _("Opening Balance"), "fieldtype": "Float", "fieldname": "opening_balance", "width": 140},
		{"label": _("New Allocated"), "fieldtype": "Float", "fieldname": "leaves_allocated", "width": 130},
		{"label": _("Leaves Taken"), "fieldtype": "Float", "fieldname": "leaves_taken", "width": 130},
		{"label": _("Expired"), "fieldtype": "Float", "fieldname": "leaves_expired", "width": 120},
		{"label": _("Closing Balance"), "fieldtype": "Float", "fieldname": "closing_balance", "width": 140},
	]


def get_data(filters):
	leave_types = get_leave_types()
	employees = get_employees(filters)

	precision = cint(frappe.db.get_single_value("System Settings", "float_precision") or 2)
	data = []

	for leave_type in leave_types:
		for emp in employees:
			row = frappe._dict()
			row.leave_type = leave_type
			row.employee = emp.name
			row.employee_name = emp.employee_name

			leaves_taken = (
				get_leaves_for_period(emp.name, leave_type, filters.from_date, filters.to_date) * -1
			)

			new_allocation, expired_leaves, cf_leaves = get_allocated_and_expired_leaves(
				filters.from_date, filters.to_date, emp.name, leave_type
			)

			opening = get_opening_balance(emp.name, leave_type, filters, cf_leaves)
			if isinstance(opening, dict):
				opening = flt(opening.get("leave_balance", 0))

			row.opening_balance = flt(opening, precision)
			row.leaves_allocated = flt(new_allocation, precision)
			row.leaves_taken = flt(leaves_taken, precision)
			row.leaves_expired = flt(expired_leaves, precision)

			closing = new_allocation + opening - (expired_leaves + leaves_taken)
			row.closing_balance = flt(closing, precision)

			data.append(row)

	return data


def get_leave_types():
	LeaveType = frappe.qb.DocType("Leave Type")
	return frappe.qb.from_(LeaveType).select(LeaveType.name).orderby(LeaveType.name).run(pluck="name")


def get_employees(filters):
	Employee = frappe.qb.DocType("Employee")
	query = frappe.qb.from_(Employee).select(Employee.name, Employee.employee_name)

	if filters.get("company"):
		query = query.where(Employee.company == filters.get("company"))

	if filters.get("department"):
		query = query.where(Employee.department == filters.get("department"))

	if filters.get("employee"):
		query = query.where(Employee.name == filters.get("employee"))

	return query.run(as_dict=True)


def get_opening_balance(employee, leave_type, filters, carry_forwarded_leaves):
	opening_balance_date = add_days(filters.from_date, -1)
	allocation = get_previous_allocation(filters.from_date, leave_type, employee)

	if (
		allocation
		and allocation.get("to_date")
		and opening_balance_date
		and getdate(allocation.get("to_date")) == getdate(opening_balance_date)
	):
		return carry_forwarded_leaves

	return get_leave_balance_on(employee, leave_type, opening_balance_date)


def get_allocated_and_expired_leaves(from_date, to_date, employee, leave_type):
	return (
		get_allocated_leaves(from_date, to_date, employee, leave_type),
		get_expired_leaves(from_date, to_date, employee, leave_type),
		get_cf_leaves(from_date, to_date, employee, leave_type),
	)


def get_allocated_leaves(from_date, to_date, employee, leave_type):
	ledger = frappe.qb.DocType("Leave Ledger Entry")
	val = (
		frappe.qb.from_(ledger)
		.select(Sum(ledger.leaves))
		.where(
			(ledger.docstatus == 1)
			& (ledger.transaction_type == "Leave Allocation")
			& (ledger.employee == employee)
			& (ledger.leave_type == leave_type)
			& ((ledger.from_date[from_date:to_date]) | (ledger.to_date[from_date:to_date]))
			& ((ledger.is_expired == 0) & (ledger.is_carry_forward == 0))
		)
	).run()[0][0]
	return val or 0.0


def get_expired_leaves(from_date, to_date, employee, leave_type):
	ledger = frappe.qb.DocType("Leave Ledger Entry")
	val = (
		frappe.qb.from_(ledger)
		.select(Abs(Sum(ledger.leaves)))
		.where(
			(ledger.docstatus == 1)
			& (ledger.transaction_type == "Leave Allocation")
			& (ledger.employee == employee)
			& (ledger.leave_type == leave_type)
			& ((ledger.from_date[from_date:to_date]) | (ledger.to_date[from_date:to_date]))
			& (ledger.is_expired == 1)
		)
	).run()[0][0]
	return val or 0.0


def get_cf_leaves(from_date, to_date, employee, leave_type):
	ledger = frappe.qb.DocType("Leave Ledger Entry")
	val = (
		frappe.qb.from_(ledger)
		.select(Sum(ledger.leaves))
		.where(
			(ledger.docstatus == 1)
			& (ledger.transaction_type == "Leave Allocation")
			& (ledger.employee == employee)
			& (ledger.leave_type == leave_type)
			& ((ledger.from_date[from_date:to_date]) | (ledger.to_date[from_date:to_date]))
			& ((ledger.is_expired == 0) & (ledger.is_carry_forward == 1))
		)
	).run()[0][0]
	return val or 0.0


def get_chart_data(data, filters):
	if not data or not filters.get("employee"):
		return None

	labels = []
	datasets = []
	leaves = []

	data = sorted(data, key=lambda k: k["employee_name"])

	for key, group in groupby(data, lambda x: x["employee_name"]):
		for g in group:
			if g.closing_balance:
				leaves.append({"leave_type": g.leave_type, "closing_balance": g.closing_balance})
		if leaves:
			labels.append(key)

	for leave in leaves:
		datasets.append({"name": leave["leave_type"], "values": [leave["closing_balance"]]})

	return {
		"data": {"labels": labels, "datasets": datasets},
		"type": "bar",
	}
