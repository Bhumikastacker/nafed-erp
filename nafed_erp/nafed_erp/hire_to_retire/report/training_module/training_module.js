// Copyright (c) 2025, CSM Technologies Pvt Ltd and contributors
// For license information, please see license.txt

frappe.query_reports["Training Module"] = {
	filters: [
        {
            fieldname: "training_requisition",
            label: "Training Requisition",
            fieldtype: "Link",
            options: "Training Requisition"
        },
		{
            fieldname: "learning_path",
            label: "Learning Path",
            fieldtype: "Link",
            options: "Learning Path"
        },
		{
            "fieldname": "expand",
            "label": "Expand Meetings",
            "fieldtype": "Check",
        }
    ]
};
