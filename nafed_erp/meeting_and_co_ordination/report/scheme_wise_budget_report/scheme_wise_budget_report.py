# Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
   
        return [
        {"label": "Scheme", "fieldname": "scheme", "fieldtype": "link", "options":"Scheme", "width": 120},
        {"label": "Branch", "fieldname": "branch", "fieldtype": "Link", "options": "Branch", "width": 140},
        {"label": "Purchase Value", "fieldname": "purchase_value", "fieldtype": "Currency", "width": 130},

        {"label": "Sale Value", "fieldname": "sale_value", "fieldtype": "Currency", "width": 130},

        {"label": "Export Value", "fieldname": "export_value", "fieldtype": "Currency", "width": 130},
        {"label": "Profit", "fieldname": "profit", "fieldtype": "Currency", "width": 120}
    ]
        


def get_data(filters):
	conditions = ["status = 'Approved'"]
	values = {}
	print("filters", filters)
	if filters.get("budget_year"):
		conditions.append("budget_year = %(budget_year)s")
		values["budget_year"] = filters["budget_year"]

	if filters.get("scheme"):
		conditions.append("scheme = %(scheme)s")
		values["scheme"] = filters["scheme"]

	if filters.get("branch"):
		conditions.append("branch = %(branch)s")
		values["branch"] = filters["branch"]

	

	where_clause = " AND ".join(conditions)

	data = frappe.db.sql(f"""
	SELECT
	scheme,
	region,
	branch,
	iot_branch,
	commodity,
	commodity_group,
	SUM(budget_purchase_qty) AS purchase_qty,
	SUM(budget_purchase_value) AS purchase_value,
	SUM(budget_sale_qty) AS sale_qty,
	SUM(budget_sale_value) AS sale_value,
	SUM(export_qty) AS export_qty,
	SUM(budget_export_value) AS export_value,
	SUM(profit) AS profit
	FROM `tabEstimated Budget Entry Form`
	WHERE {where_clause}
	GROUP BY scheme,branch
	ORDER BY branch
	""", values, as_dict=True)
	print(data)
	return data

