# Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from itertools import groupby


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
   
      return [
    {
        "label": "Commodity Group",
        "fieldname": "commodity_group",
        "fieldtype": "Data",
        "width": 160
    },
    {
        "label": "Scheme",
        "fieldname": "scheme",
        "fieldtype": "Data",
        "width": 120
    },
    {
        "label": "PURCHASE",
        "fieldname": "total_purchase",
      #  "fieldtype": "Currency",
        "width": 130
    },
    {
        "label": "SALES",
        "fieldname": "total_sale",
       # "fieldtype": "Currency",
        "width": 130
    },
    {
        "label": "IMPORT/EXPORT",
        "fieldname": "total_export",
      #  "fieldtype": "Currency",
        "width": 160
    },
    {
        "label": "PROFIT",
        "fieldname": "total_profit",
      #  "fieldtype": "Currency",
        "width": 150
    }
]


				


def get_data(filters):

    data = []
    values = {}
    base_conditions = ["status = 'Approved'"]

    commodity_groups = frappe.get_all("Commodity Type", pluck="name")

    # Filters
    if filters.get("budget_year"):
        base_conditions.append("budget_year = %(budget_year)s")
        values["budget_year"] = filters["budget_year"]

    if filters.get("branch"):
        base_conditions.append("branch = %(branch)s")
        values["branch"] = filters["branch"]

    # Grand totals
    grand_purchase = 0
    grand_sale = 0
    grand_export = 0
    grand_profit = 0

    for group in commodity_groups:

        conditions = base_conditions + ["commodity_group = %(commodity_group)s"]
        where_clause = " AND ".join(conditions)

        values["commodity_group"] = group


        

        group_data = frappe.db.sql(f"""
    -- Scheme level rows
            SELECT 
                '' AS commodity_group,
                scheme,
                SUM(budget_purchase_value) AS total_purchase,
                SUM(budget_sale_value) AS total_sale,
                SUM(budget_export_value) AS total_export,
                SUM(profit) AS total_profit
            FROM `tabEstimated Budget Entry Form`
            WHERE {where_clause}
            GROUP BY scheme

            UNION ALL

            -- Subtotal row
            SELECT 
                '' AS commodity_group,
                'Subtotal' AS scheme,
                SUM(budget_purchase_value) AS total_purchase,
                SUM(budget_sale_value) AS total_sale,
                SUM(budget_export_value) AS total_export,
                SUM(profit) AS total_profit
            FROM `tabEstimated Budget Entry Form`
            WHERE {where_clause}
        """, values, as_dict=True)
    
        

        if group_data[0]['total_purchase']:
            data.append({
            "commodity_group": group,
            "scheme": "",
            "total_purchase": "",
            "total_sale": "",
            "total_export": "",
            "total_profit": ""
            })
            data.extend(group_data)
            for row in group_data:
                print("ddddddddddddddddddddd", row)
                if row["scheme"] == "Subtotal":
                    grand_purchase += row["total_purchase"] or 0
                    grand_sale += row["total_sale"] or 0
                    grand_export += row["total_export"] or 0
                    grand_profit += row["total_profit"] or 0
                    
                    data.append({
            "commodity_group": "",
            "scheme": "",
            "total_purchase": "",
            "total_sale": "",
            "total_export": "",
            "total_profit": ""
            })


    data.append({
        "commodity_group": "Grand Total",
        "scheme": "",
        "total_purchase": grand_purchase,
        "total_sale": grand_sale,
        "total_export": grand_export,
        "total_profit": grand_profit
    })

    return data






