# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


import frappe
from frappe import _
from frappe.utils import flt

import erpnext

salary_slip = frappe.qb.DocType("Salary Slip")
salary_detail = frappe.qb.DocType("Salary Detail")
salary_component = frappe.qb.DocType("Salary Component")

def get_custom_deduction_components(employee_list):
    if not employee_list:
        return []
    data = frappe.db.sql("""
        SELECT parent, deduction, SUM(amount) as total
        FROM `tabSalary Deduction`
        WHERE parent IN %(employees)s
        GROUP BY parent, deduction
    """, {"employees": tuple(employee_list)}, as_dict=True)

    # collect only components with value > 0
    components = set()
    for d in data:
        if d.total > 0:
            components.add(d.deduction)

    return list(components)

def get_custom_deduction_map(employee_list):
    if not employee_list:
        return {}

    result = frappe.db.sql("""
        SELECT parent, deduction, SUM(amount) as amount
        FROM `tabSalary Deduction`
        WHERE parent IN %(employees)s
        GROUP BY parent, deduction
    """, {"employees": tuple(employee_list)}, as_dict=True)

    emp_map = {}

    for d in result:
        emp_map.setdefault(d.parent, {})
        emp_map[d.parent][d.deduction] = d.amount

    return emp_map

def get_employee_custom_total(employee):
    return frappe.db.sql("""
        SELECT SUM(amount)
        FROM `tabSalary Deduction`
        WHERE parent = %s AND parenttype = 'Employee'
    """, (employee), as_list=True)[0][0] or 0

def execute(filters=None):
	print("CORE SALARY REGISTER RUNNING")
	if not filters:
		filters = {}

	currency = None
	if filters.get("currency"):
		currency = filters.get("currency")
	company_currency = erpnext.get_company_currency(filters.get("company"))

	salary_slips = get_salary_slips(filters, company_currency)
	employee_list = [ss.employee for ss in salary_slips]

	custom_components = get_custom_deduction_components(employee_list)
	custom_ded_map = get_custom_deduction_map(employee_list)
	if not salary_slips:
			return [], []

	earning_types, ded_types = get_earning_and_deduction_types(salary_slips)


	ss_earning_map = get_salary_slip_details(salary_slips, currency, company_currency, "earnings")
	ss_ded_map = get_salary_slip_details(salary_slips, currency, company_currency, "deductions")
		# ✅ FILTER HERE
	filtered_ded_types = []
	for d in ded_types:
		if any(ss_ded_map.get(ss.name, {}).get(d, 0) > 0 for ss in salary_slips):
			filtered_ded_types.append(d)

	ded_types = filtered_ded_types

	columns = get_columns(earning_types, ded_types, custom_components)
	doj_map = get_employee_doj_map()

	data = []
	
	for ss in salary_slips:
		custom_deduction = get_employee_custom_total(ss.employee)
	

		row = {
			"salary_slip_id": ss.name,
			"employee": ss.employee,
			"employee_name": ss.employee_name,
			"data_of_joining": doj_map.get(ss.employee),
			"branch": ss.branch,
			"department": ss.department,
			"designation": ss.designation,
			"company": ss.company,
			"start_date": ss.start_date,
			"end_date": ss.end_date,
			"leave_without_pay": ss.leave_without_pay,
			"absent_days": ss.absent_days,
			"payment_days": ss.payment_days,
			"currency": currency or company_currency,
			"total_loan_repayment": ss.total_loan_repayment,
			"custom_deduction": custom_deduction,
		}

		update_column_width(ss, columns)

		for e in earning_types:
			row.update({frappe.scrub(e): ss_earning_map.get(ss.name, {}).get(e)})

		for d in ded_types:
			row.update({frappe.scrub(d): ss_ded_map.get(ss.name, {}).get(d)})

		# ADD CUSTOM DEDUCTION VALUES
		for comp in custom_components:
			row["custom_" + frappe.scrub(comp)] = custom_ded_map.get(ss.employee, {}).get(comp, 0)	

		if currency == company_currency:
			row.update(
				{
					"gross_pay": flt(ss.gross_pay) * flt(ss.exchange_rate),
					"total_deduction": flt(ss.total_deduction)* flt(ss.exchange_rate),
					"net_pay": flt(ss.net_pay) * flt(ss.exchange_rate),
				}
			)

		else:
			row.update(
				{
					"gross_pay": ss.gross_pay,
					"total_deduction": flt(ss.total_deduction),
					"net_pay": ss.net_pay,
				}
			)

	data.append(row)

	# -----------
	# ADD GRADE 
	# -----------

	employee_list = list({d.get("employee") for d in data if d.get("employee")})

	# Fetch Employee Grade
	emp_map = {}
	if employee_list:
		emp_data = frappe.get_all(
			"Employee",
			filters={"name": ["in", employee_list]},
			fields=["name", "grade"]
		)
		emp_map = {e.name: e.grade for e in emp_data}



	# Update rows
	# for row in data:
		row["grade"] = emp_map.get(row.get("employee"))
		# row["basic_pay"] = basic_map.get(row.get("salary_slip_id"), 0)

	return columns, data




def get_earning_and_deduction_types(salary_slips):
	salary_component_and_type = {_("Earning"): [], _("Deduction"): []}

	for salary_component in get_salary_components(salary_slips):
		component_type = get_salary_component_type(salary_component)
		salary_component_and_type[_(component_type)].append(salary_component)

	return sorted(salary_component_and_type[_("Earning")]), sorted(salary_component_and_type[_("Deduction")])


def update_column_width(ss, columns):
	if ss.branch is not None:
		columns[3].update({"width": 120})
	if ss.department is not None:
		columns[4].update({"width": 120})
	if ss.designation is not None:
		columns[5].update({"width": 120})
	if ss.leave_without_pay is not None:
		columns[9].update({"width": 120})


def get_columns(earning_types, ded_types, custom_components):
	columns = [
		{
			"label": _("Salary Slip ID"),
			"fieldname": "salary_slip_id",
			"fieldtype": "Link",
			"options": "Salary Slip",
			"width": 150,
		},
		{
			"label": _("Employee"),
			"fieldname": "employee",
			"fieldtype": "Link",
			"options": "Employee",
			"width": 120,
		},
		{
			"label": _("Employee Name"),
			"fieldname": "employee_name",
			"fieldtype": "Data",
			"width": 140,
		},
		{
			"label": _("Date of Joining"),
			"fieldname": "data_of_joining",
			"fieldtype": "Date",
			"width": 80,
		},
		{
			"label": _("Branch"),
			"fieldname": "branch",
			"fieldtype": "Link",
			"options": "Branch",
			"width": -1,
		},
		{
			"label": _("Department"),
			"fieldname": "department",
			"fieldtype": "Link",
			"options": "Department",
			"width": -1,
		},
		{
			"label": _("Designation"),
			"fieldname": "designation",
			"fieldtype": "Link",
			"options": "Designation",
			"width": 120,
		},
		{
			"label": _("Company"),
			"fieldname": "company",
			"fieldtype": "Link",
			"options": "Company",
			"width": 120,
		},
		{
			"label": _("Start Date"),
			"fieldname": "start_date",
			"fieldtype": "Data",
			"width": 80,
		},
		{
			"label": _("End Date"),
			"fieldname": "end_date",
			"fieldtype": "Data",
			"width": 80,
		},
		{
			"label": _("Leave Without Pay"),
			"fieldname": "leave_without_pay",
			"fieldtype": "Float",
			"width": 50,
		},
		{
			"label": _("Absent Days"),
			"fieldname": "absent_days",
			"fieldtype": "Float",
			"width": 50,
		},
		{
			"label": _("Payment Days"),
			"fieldname": "payment_days",
			"fieldtype": "Float",
			"width": 120,
		},
		{
		"label": _("Grade"),
		"fieldname": "grade",
		"fieldtype": "Data",
		"width": 120
	    },
	]

	for earning in earning_types:
		columns.append(
			{
				"label": earning,
				"fieldname": frappe.scrub(earning),
				"fieldtype": "Currency",
				"options": "currency",
				"width": 120,
			}
		)

	columns.append(
		{
			"label": _("Gross Pay"),
			"fieldname": "gross_pay",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120,
		}
		)
	
		# ADD CUSTOM DEDUCTION COLUMNS
	for comp in custom_components:
		columns.append(
			{
				"label": comp,
				"fieldname": "custom_" + frappe.scrub(comp),
				"fieldtype": "Currency",
				"options": "currency",
				"width": 120,
			}
		)

	for deduction in ded_types:
		columns.append(
			{
				"label": deduction,
				"fieldname": frappe.scrub(deduction),
				"fieldtype": "Currency",
				"options": "currency",
				"width": 120,
			}
		)

	if "lending" in frappe.get_installed_apps():
		columns.append(
			{
				"label": _("Loan Repayment"),
				"fieldname": "total_loan_repayment",
				"fieldtype": "Currency",
				"options": "currency",
				"width": 120,
			}
		)

	columns.extend(
		[    
			{
				"label": _("Total Deduction"),
				"fieldname": "total_deduction",
				"fieldtype": "Currency",
				"options": "currency",
				"width": 120,
			},
			{
				"label": _("Net Pay"),
				"fieldname": "net_pay",
				"fieldtype": "Currency",
				"options": "currency",
				"width": 120,
			},
			{
				"label": _("Currency"),
				"fieldtype": "Data",
				"fieldname": "currency",
				"options": "Currency",
				"hidden": 1,
			},
		]
	)
	return columns


def get_salary_components(salary_slips):
	return (
		frappe.qb.from_(salary_detail)
		.where((salary_detail.amount != 0) & (salary_detail.parent.isin([d.name for d in salary_slips])))
		.select(salary_detail.salary_component)
		.distinct()
	).run(pluck=True)


def get_salary_component_type(salary_component):
	return frappe.db.get_value("Salary Component", salary_component, "type", cache=True)


def get_salary_slips(filters, company_currency):
	doc_status = {"Draft": 0, "Submitted": 1, "Cancelled": 2}

	query = frappe.qb.from_(salary_slip).select(salary_slip.star)

	if filters.get("docstatus"):
		query = query.where(salary_slip.docstatus == doc_status[filters.get("docstatus")])

	if filters.get("from_date"):
		query = query.where(salary_slip.start_date >= filters.get("from_date"))

	if filters.get("to_date"):
		query = query.where(salary_slip.end_date <= filters.get("to_date"))

	if filters.get("company"):
		query = query.where(salary_slip.company == filters.get("company"))

	if filters.get("employee"):
		query = query.where(salary_slip.employee == filters.get("employee"))

	if filters.get("currency") and filters.get("currency") != company_currency:
		query = query.where(salary_slip.currency == filters.get("currency"))

	if filters.get("department"):
		query = query.where(salary_slip.department == filters["department"])

	if filters.get("designation"):
		query = query.where(salary_slip.designation == filters["designation"])

	if filters.get("branch"):
		query = query.where(salary_slip.branch == filters["branch"])

	salary_slips = query.run(as_dict=1)

	return salary_slips or []


def get_employee_doj_map():
	employee = frappe.qb.DocType("Employee")

	result = (frappe.qb.from_(employee).select(employee.name, employee.date_of_joining)).run()

	return frappe._dict(result)


def get_salary_slip_details(salary_slips, currency, company_currency, component_type):
	salary_slips = [ss.name for ss in salary_slips]

	result = (
		frappe.qb.from_(salary_slip)
		.join(salary_detail)
		.on(salary_slip.name == salary_detail.parent)
		.where((salary_detail.parent.isin(salary_slips)) & (salary_detail.parentfield == component_type))
		.select(
			salary_detail.parent,
			salary_detail.salary_component,
			salary_detail.amount,
			salary_slip.exchange_rate,
		)
	).run(as_dict=1)

	ss_map = {}

	for d in result:
		ss_map.setdefault(d.parent, frappe._dict()).setdefault(d.salary_component, 0.0)
		if currency == company_currency:
			ss_map[d.parent][d.salary_component] += flt(d.amount) * flt(
				d.exchange_rate if d.exchange_rate else 1
			)
		else:
			ss_map[d.parent][d.salary_component] += flt(d.amount)

	return ss_map

