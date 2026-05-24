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

    # Filters
    if filters.get("budget_year"):
        base_conditions.append("budget_year = %(budget_year)s")
        values["budget_year"] = filters["budget_year"]

    if filters.get("branch"):
        base_conditions.append("branch = %(branch)s")
        values["branch"] = filters["branch"]

    if filters.get("commodity_group"):
        base_conditions.append("commodity_group = %(commodity_group)s")
        values["commodity_group"] = filters["commodity_group"]
        

    if filters.get("scheme"):
        base_conditions.append("scheme = %(scheme)s")
        values["scheme"] = filters["scheme"]

    # Decide groups
    if filters.get("commodity_group"):
        commodity_groups = [filters.get("commodity_group")]
    else:
        commodity_groups = frappe.get_all("Commodity Type", pluck="name")

    # Grand totals
    grand_purchase = 0
    grand_sale = 0
    grand_export = 0
    grand_profit = 0

    for group in commodity_groups:

        # Create local copy of values (IMPORTANT)
        local_values = values.copy()
        local_values["commodity_group"] = group

        conditions = base_conditions + ["commodity_group = %(commodity_group)s"]
        where_clause = " AND ".join(conditions)

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
        """, local_values, as_dict=True)

        # ✅ Safe check
        if not group_data:
            continue

        subtotal_row = next((r for r in group_data if r["scheme"] == "Subtotal"), None)

        # Skip empty groups
        if not subtotal_row or not subtotal_row["total_purchase"]:
            continue

        # Group header
        data.append({
            "commodity_group": group,
            "scheme": "",
            "total_purchase": "",
            "total_sale": "",
            "total_export": "",
            "total_profit": ""
        })

        # Add rows
        data.extend(group_data)

        # Add to grand total
        grand_purchase += subtotal_row["total_purchase"] or 0
        grand_sale += subtotal_row["total_sale"] or 0
        grand_export += subtotal_row["total_export"] or 0
        grand_profit += subtotal_row["total_profit"] or 0

    # Grand total
    data.append({
        "commodity_group": "Grand Total",
        "scheme": "",
        "total_purchase": grand_purchase,
        "total_sale": grand_sale,
        "total_export": grand_export,
        "total_profit": grand_profit
    })

    return data
