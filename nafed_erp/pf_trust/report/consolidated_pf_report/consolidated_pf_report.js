// Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
// For license information, please see license.txt


frappe.query_reports["Consolidated PF Report"] = {
    filters: [
        {
            fieldname: "company",
            label: __("Company"),
            fieldtype: "MultiSelectList",
            options: "Company",
            get_data: function (txt) {
                return frappe.db.get_link_options("Company", txt);
            }
        },
        {
            fieldname: "from_date",
            label: __("From Date"),
            fieldtype: "Date",
            reqd: 1
        },
        {
            fieldname: "to_date",
            label: __("To Date"),
            fieldtype: "Date",
            reqd: 1
        }
    ]
};
