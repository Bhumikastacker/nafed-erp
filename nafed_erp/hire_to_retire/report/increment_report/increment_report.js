frappe.query_reports["Increment Report"] = {
    filters: [
        {
            fieldname: "company",
            label: "Company",
            fieldtype: "MultiSelectList",
            get_data: function(txt) {
                return frappe.db.get_link_options("Company", txt);
            },
            reqd: 1
        },
        {
            fieldname: "month",
            label: "Month",
            fieldtype: "Select",
            options: "\nJanuary\nJuly",
            reqd: 1
        }
    ]
};