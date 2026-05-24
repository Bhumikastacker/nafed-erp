frappe.query_reports["State-wise Nominations Received"] = {
    filters: [
        {
            fieldname: "application_received_start",
            label: __("Application Received Start Date"),
            fieldtype: "Date"
        },
        {
            fieldname: "application_received_end",
            label: __("Application Received End Date"),
            fieldtype: "Date"
        }
    ]
};