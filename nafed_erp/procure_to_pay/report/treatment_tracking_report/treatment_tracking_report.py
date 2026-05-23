# Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):

    columns = get_columns()

    data = get_data(filters)

    return columns, data


def get_columns():

    return [

        {
            "label": "Warehouse",
            "fieldname": "warehouse",
            "fieldtype": "Data",
            "width": 180
        },

        {
            "label": "Treatment Type",
            "fieldname": "treatment_type",
            "fieldtype": "Data",
            "width": 150
        },

        {
            "label": "Scheduled Date",
            "fieldname": "scheduled_date",
            "fieldtype": "Date",
            "width": 120
        },

        {
            "label": "Actual Treatment Date",
            "fieldname": "actual_treatment_date",
            "fieldtype": "Date",
            "width": 150
        },

        {
            "label": "Next Due Date",
            "fieldname": "next_due_date",
            "fieldtype": "Date",
            "width": 120
        },

        {
            "label": "Treatment Status",
            "fieldname": "treatment_status",
            "fieldtype": "Data",
            "width": 140
        },

        {
            "label": "Remarks",
            "fieldname": "observation_remarks",
            "fieldtype": "Data",
            "width": 250
        }
    ]


def get_data(filters):

    conditions = ""

    if filters.get("warehouse"):
        conditions += f"""
            AND fs.warehouse = '{filters.get("warehouse")}'
        """

    if filters.get("treatment_type"):
        conditions += f"""
            AND fs.treatment_type = '{filters.get("treatment_type")}'
        """

    if filters.get("status"):
        conditions += f"""
            AND te.treatment_status = '{filters.get("status")}'
        """

    if filters.get("from_date"):
        conditions += f"""
            AND fs.scheduled_date >= '{filters.get("from_date")}'
        """

    if filters.get("to_date"):
        conditions += f"""
            AND fs.scheduled_date <= '{filters.get("to_date")}'
        """

    data = frappe.db.sql(f"""

        SELECT

            fs.warehouse,
            fs.treatment_type,
            fs.scheduled_date,
            te.actual_treatment_date,
            fs.next_due_date,
            te.treatment_status,
            te.observation_remarks

        FROM
            `tabFumigation Schedule` fs

        LEFT JOIN
            `tabTreatment Execution` te

        ON
            fs.name = te.schedule_reference

        WHERE
            1 = 1

            {conditions}

    """, as_dict=1)

    return data