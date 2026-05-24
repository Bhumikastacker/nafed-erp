// Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
// For license information, please see license.txt

frappe.query_reports["Treatment Tracking Report"] = {

    filters: [

        {
            fieldname: "warehouse",
            label: "Warehouse",
            fieldtype: "Link",
            options: "Warehouse"
        },

        {
            fieldname: "treatment_type",
            label: "Treatment Type",
            fieldtype: "Select",
            options: "\nFumigation\nRodent Control\nBoth"
        },

        {
            fieldname: "status",
            label: "Status",
            fieldtype: "Select",
            options: "\nCompleted\nScheduled\nDeferred"
        },

        {
            fieldname: "from_date",
            label: "From Date",
            fieldtype: "Date"
        },

        {
            fieldname: "to_date",
            label: "To Date",
            fieldtype: "Date"
        }
    ]
};