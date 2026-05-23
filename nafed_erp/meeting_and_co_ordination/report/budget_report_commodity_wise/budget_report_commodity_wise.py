# Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
   
        return [
      #  {"label": "Region", "fieldname": "region", "fieldtype": "Data", "options":"Zone", "width": 120},
      #  {"label": "Branch", "fieldname": "branch", "fieldtype": "Link", "options": "Branch", "width": 140},
     #   {"label": "IoT Branch", "fieldname": "iot_branch", "fieldtype": "Data",  "width": 150},
        {"label": "Commodity", "fieldname": "commodity", "fieldtype": "Link", "options": "Commodity", "width": 120},
     #   {"label": "Purchase Qty", "fieldname": "purchase_qty", "fieldtype": "Float", "width": 110},
     

        {"label": "Purchase Value", "fieldname": "purchase_value", "fieldtype": "Currency", "width": 130},
     #   {"label": "Sale Qty", "fieldname": "sale_qty", "fieldtype": "Float", "width": 110},
        {"label": "Sale Value", "fieldname": "sale_value", "fieldtype": "Currency", "width": 130},
     #   {"label": "Export Qty", "fieldname": "export_qty", "fieldtype": "Float", "width": 110},
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

	

	if filters.get("branch"):
		conditions.append("branch = %(branch)s")
		values["branch"] = filters["branch"]

	

	if filters.get("commodity"):
		conditions.append("commodity = %(commodity)s")
		values["commodity"] = filters["commodity"]
		
	

	where_clause = " AND ".join(conditions)



	return frappe.db.sql(f"""
		SELECT
		region,
		branch,
		iot_branch,
		commodity,
		commodity_group,

		SUM(budget_purchase_value) AS purchase_value,

		SUM(budget_sale_value) AS sale_value,

		SUM(budget_export_value) AS export_value,
		SUM(profit) AS profit
		FROM `tabEstimated Budget Entry Form`
		WHERE {where_clause}
		GROUP BY commodity
		ORDER BY  commodity
		""", values, as_dict=True)

