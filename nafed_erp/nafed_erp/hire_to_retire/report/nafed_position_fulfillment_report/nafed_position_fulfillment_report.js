// Copyright (c) 2025, CSM Technologies Pvt Ltd and contributors
// For license information, please see license.txt

frappe.query_reports["Nafed Position Fulfillment Report"] = {
	filters: [
        {
            fieldname: "company",
            label: "Company",
            fieldtype: "Link",
            options: "Company"
        },
        {
            fieldname: "department",
            label: "Department",
            fieldtype: "Link",
            options: "Department"
        },
        {
            fieldname: "designation",
            label: "Designation",
            fieldtype: "Link",
            options: "Designation"
        },
        {
            fieldname: "show_details",
            label: "Show Full Details",
            fieldtype: "Check"
        }
    ]
};
