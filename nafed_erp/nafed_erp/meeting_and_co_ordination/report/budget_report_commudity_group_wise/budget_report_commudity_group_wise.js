// Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
// For license information, please see license.txt

frappe.query_reports["Budget Report Commudity Group Wise"] = {
	filters: [
        {
            fieldname: "budget_year",
            label: "Budget Year",
            fieldtype: "Link",
            options: "budgetary year",
            reqd: 1
        },
        
        {
            fieldname: "branch",
            label: "Branch",
            fieldtype: "Link",
            options: "Company"
        },
        
        {
            fieldname: "commodity_group",
            label: "Commodity Group",
            fieldtype: "Link",
            options: "Commodity Type"
        }
        
    ]
};
