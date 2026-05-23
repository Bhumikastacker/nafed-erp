// Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
// For license information, please see license.txt

// frappe.query_reports["Accrued interest sheet"] = {
// 	"filters": [

// 	]
// };

frappe.query_reports["Accrued interest sheet"] = {
	"filters": [
		// Filter 1: As on Date
		// This date is used to calculate interest up to this day
		{
			"fieldname": "to_date",
			"label": __("As on Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1
		},

		// Filter 1: As on Date
		// This date is used to calculate interest up to this day
		{
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("company")
		},

		// Filter 3: Interest Mode
		// Filters investments based on interest calculation frequency
		{
			"fieldname": "interest_mode",
			"label": __("Interest Mode"),
			"fieldtype": "Select",
			"options": "\nYearly\nHalf Yearly\nQuarterly\nMonthly"
		},

		// Filter 4: Particulars (Investment)
		// Allows user to filter report by specific investment
		{
			"fieldname": "investment",
			"label": __("Particulars"),
			"fieldtype": "Link",
			"options": "Investment"
		},

		// Filter 5: Security (Investment)
		// Allows user to filter report by specific Security
		{
			"fieldname": "name_of_security",
			"label": __("Security",),
			"fieldtype": "Data",
		}
	]
};
