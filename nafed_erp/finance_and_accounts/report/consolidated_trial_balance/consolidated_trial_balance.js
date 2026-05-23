frappe.query_reports["Consolidated Trial Balance"] = {
    filters: [
        {
            fieldname: "parent_company",
            label: __("Parent Company"),
            fieldtype: "Link",
            options: "Company",
            reqd: 1,
            get_data: function(txt) {
                // fetch only group companies
                return frappe.db.get_link_options("Company", txt, { is_group: 1 });
            },
            on_change: function(report) {
                frappe.query_report.set_filter_value("child_companies", []);
            }
        },
        {
            fieldname: "child_companies",
            label: __("Child Companies"),
            fieldtype: "MultiSelectList",
            get_data: async function(txt) {
                const parent = frappe.query_report.get_filter_value("parent_company");
                if (!parent) return [];
                // fetch only non-group companies where parent_company = selected parent
                return frappe.db.get_link_options("Company", txt, { parent_company: parent, is_group: 0 });
            }
        },
        {
            fieldname: "fiscal_year",
            label: __("Fiscal Year"),
            fieldtype: "Link",
            options: "Fiscal Year",
            default: erpnext.utils.get_fiscal_year(frappe.datetime.get_today()),
            reqd: 1,
            on_change: function(report) {
                var fiscal_year = report.get_values().fiscal_year;
                if (!fiscal_year) return;
                frappe.model.with_doc("Fiscal Year", fiscal_year, function() {
                    var fy = frappe.model.get_doc("Fiscal Year", fiscal_year);
                    frappe.query_report.set_filter_value({
                        from_date: fy.year_start_date,
                        to_date: fy.year_end_date
                    });
                });
            }
        },
        {
            fieldname: "from_date",
            label: __("From Date"),
            fieldtype: "Date",
            default: erpnext.utils.get_fiscal_year(frappe.datetime.get_today(), true)[1]
        },
        {
            fieldname: "to_date",
            label: __("To Date"),
            fieldtype: "Date",
            default: erpnext.utils.get_fiscal_year(frappe.datetime.get_today(), true)[2]
        },
        {
			fieldname: "cost_center",
			label: __("Cost Center"),
			fieldtype: "Link",
			options: "Cost Center",
			get_query: function() {
				let parent_company = frappe.query_report.get_filter_value("parent_company");
				let child_companies = frappe.query_report.get_filter_value("child_companies") || [];
		
				// Ensure child_companies is always an array
				if (typeof child_companies === "string") {
					child_companies = [child_companies];
				}
		
				// Build company list
				let companies = [parent_company].concat(child_companies);
		
				return {
					doctype: "Cost Center",
					filters: {
						company: ["in", companies]
					}
				};
			}
		},		
        {
			fieldname: "project",
			label: __("Project"),
			fieldtype: "Link",
			options: "Project",
			get_query: function() {
				let parent_company = frappe.query_report.get_filter_value("parent_company");
				let child_companies = frappe.query_report.get_filter_value("child_companies") || [];
		
				// Ensure child_companies is an array
				if (typeof child_companies === "string") {
					child_companies = [child_companies];
				}
		
				// Combine parent + children
				let companies = [parent_company].concat(child_companies);
		
				return {
					doctype: "Project",
					filters: {
						company: ["in", companies]
					}
				};
			}
		},
        {
            fieldname: "finance_book",
            label: __("Finance Book"),
            fieldtype: "Link",
            options: "Finance Book"
        },
        {
            fieldname: "presentation_currency",
            label: __("Currency"),
            fieldtype: "Select",
            options: erpnext.get_presentation_currency_list()
        },
        {
            fieldname: "with_period_closing_entry_for_opening",
            label: __("With Period Closing Entry For Opening Balances"),
            fieldtype: "Check",
            default: 1
        },
        {
            fieldname: "with_period_closing_entry_for_current_period",
            label: __("Period Closing Entry For Current Period"),
            fieldtype: "Check",
            default: 1
        },
        {
            fieldname: "show_zero_values",
            label: __("Show zero values"),
            fieldtype: "Check"
        },
        {
            fieldname: "show_unclosed_fy_pl_balances",
            label: __("Show unclosed fiscal year's P&L balances"),
            fieldtype: "Check"
        },
        {
            fieldname: "include_default_book_entries",
            label: __("Include Default FB Entries"),
            fieldtype: "Check",
            default: 1
        },
        {
            fieldname: "show_net_values",
            label: __("Show net values in opening and closing columns"),
            fieldtype: "Check",
            default: 1
        }
    ],
    formatter: erpnext.financial_statements.formatter,
    tree: true,
    name_field: "account",
    parent_field: "parent_account",
    initial_depth: 3
};

erpnext.utils.add_dimensions("Consolidated Trial Balance", 6);
