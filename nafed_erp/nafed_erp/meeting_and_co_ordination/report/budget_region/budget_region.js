// Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
// For license information, please see license.txt

frappe.query_reports["Budget Region"] = {
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
            fieldname: "region",
            label: "Region",
            fieldtype: "Link",
            options: "Zone"
        }
       
    ]
};
