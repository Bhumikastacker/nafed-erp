// -------------------------------
// Helper: fetch options for MULTIPLE companies
// -------------------------------
async function get_multi_company_link_options(doctype, txt, companies) {
    if (!companies || !companies.length) {
        return frappe.db.get_link_options(doctype, txt);
    }

    let all_options = [];

    for (let c of companies) {
        let opts = await frappe.db.get_link_options(doctype, txt, { company: c });
        all_options = all_options.concat(opts);
    }

    // Deduplicate by "value"
    let unique = {};
    all_options.forEach(o => { unique[o.value] = o; });

    return Object.values(unique);
}

// -------------------------------
// Main Report
// -------------------------------
frappe.query_reports["Consolidated General Ledger"] = {
    filters: [
        {
            fieldname: "company",
            label: __("Company"),
            fieldtype: "MultiSelectList",
            reqd: 1,
            get_data: function (txt) {
                return frappe.db.get_link_options("Company", txt);
            },
        },

        {
            fieldname: "finance_book",
            label: __("Finance Book"),
            fieldtype: "Link",
            options: "Finance Book",
        },

        {
            fieldname: "from_date",
            label: __("From Date"),
            fieldtype: "Date",
            default: frappe.datetime.add_months(frappe.datetime.get_today(), -1),
            reqd: 1,
        },

        {
            fieldname: "to_date",
            label: __("To Date"),
            fieldtype: "Date",
            default: frappe.datetime.get_today(),
            reqd: 1,
        },

        // -------------------------------
        // Account (MULTI-COMPANY)
        // -------------------------------
        {
            fieldname: "account",
            label: __("Account"),
            fieldtype: "MultiSelectList",
            get_data: async function (txt) {
                let companies = frappe.query_report.get_filter_value("company");

                if (typeof companies === "string") {
                    companies = companies.split(",").map(c => c.trim());
                }

                return await get_multi_company_link_options("Account", txt, companies);
            },
        },

        {
            fieldname: "voucher_no",
            label: __("Voucher No"),
            fieldtype: "Data",
            on_change: function () {
                frappe.query_report.set_filter_value(
                    "categorize_by",
                    "Categorize by Voucher (Consolidated)"
                );
            },
        },

        {
            fieldname: "against_voucher_no",
            label: __("Against Voucher No"),
            fieldtype: "Data",
        },

        { fieldtype: "Break" },

        // -------------------------------
        // Party Type
        // -------------------------------
        {
            fieldname: "party_type",
            label: __("Party Type"),
            fieldtype: "Autocomplete",
            options: Object.keys(frappe.boot.party_account_types),
            on_change: function () {
                frappe.query_report.set_filter_value("party", []);
            },
        },

        // -------------------------------
        // Party (MULTI)
        // -------------------------------
        {
            fieldname: "party",
            label: __("Party"),
            fieldtype: "MultiSelectList",
            get_data: async function (txt) {
                let party_type = frappe.query_report.get_filter_value("party_type");
                if (!party_type) return;

                return await frappe.db.get_link_options(party_type, txt);
            },
            on_change: function () {
                let party_type = frappe.query_report.get_filter_value("party_type");
                let parties = frappe.query_report.get_filter_value("party");

                if (!party_type || !parties || parties.length !== 1) {
                    frappe.query_report.set_filter_value("party_name", "");
                    frappe.query_report.set_filter_value("tax_id", "");
                    return;
                }

                let party = parties[0];
                let fieldname = erpnext.utils.get_party_name(party_type) || "name";

                frappe.db.get_value(party_type, party, fieldname, (value) => {
                    frappe.query_report.set_filter_value("party_name", value[fieldname]);
                });

                if (["Customer", "Supplier"].includes(party_type)) {
                    frappe.db.get_value(party_type, party, "tax_id", (value) => {
                        frappe.query_report.set_filter_value("tax_id", value["tax_id"]);
                    });
                }
            },
        },

        {
            fieldname: "party_name",
            label: __("Party Name"),
            fieldtype: "Data",
            hidden: 1
        },

        {
            fieldname: "categorize_by",
            label: __("Categorize by"),
            fieldtype: "Select",
            options: [
                "",
                { label: __("Categorize by Voucher"), value: "Categorize by Voucher" },
                {
                    label: __("Categorize by Voucher (Consolidated)"),
                    value: "Categorize by Voucher (Consolidated)",
                },
                { label: __("Categorize by Account"), value: "Categorize by Account" },
                { label: __("Categorize by Party"), value: "Categorize by Party" },
            ],
            default: "Categorize by Voucher (Consolidated)",
        },

        { fieldname: "tax_id", label: __("Tax Id"), fieldtype: "Data", hidden: 1 },

        {
            fieldname: "presentation_currency",
            label: __("Currency"),
            fieldtype: "Select",
            options: erpnext.get_presentation_currency_list(),
        },

        // -------------------------------
        // Cost Center (MULTI-COMPANY)
        // -------------------------------
        {
            fieldname: "cost_center",
            label: __("Cost Center"),
            fieldtype: "MultiSelectList",
            get_data: async function (txt) {
                let companies = frappe.query_report.get_filter_value("company");

                if (typeof companies === "string") {
                    companies = companies.split(",").map(c => c.trim());
                }

                return await get_multi_company_link_options("Cost Center", txt, companies);
            },
        },

        // -------------------------------
        // Project (MULTI-COMPANY)
        // -------------------------------
        {
            fieldname: "project",
            label: __("Project"),
            fieldtype: "MultiSelectList",
            get_data: async function (txt) {
                let companies = frappe.query_report.get_filter_value("company");

                if (typeof companies === "string") {
                    companies = companies.split(",").map(c => c.trim());
                }

                return await get_multi_company_link_options("Project", txt, companies);
            },
        },

        { fieldname: "include_dimensions", label: __("Consider Accounting Dimensions"), fieldtype: "Check", default: 1 },
        { fieldname: "show_opening_entries", label: __("Show Opening Entries"), fieldtype: "Check" },
        { fieldname: "include_default_book_entries", label: __("Include Default FB Entries"), fieldtype: "Check", default: 1 },
        { fieldname: "show_cancelled_entries", label: __("Show Cancelled Entries"), fieldtype: "Check" },
        { fieldname: "show_net_values_in_party_account", label: __("Show Net Values in Party Account"), fieldtype: "Check" },
        { fieldname: "show_amount_in_company_currency", label: __("Show Credit / Debit in Company Currency"), fieldtype: "Check" },
        { fieldname: "add_values_in_transaction_currency", label: __("Add Columns in Transaction Currency"), fieldtype: "Check" },
        { fieldname: "show_remarks", label: __("Show Remarks"), fieldtype: "Check" },
        { fieldname: "ignore_err", label: __("Ignore Exchange Rate Revaluation and Gain / Loss Journals"), fieldtype: "Check" },
        { fieldname: "ignore_cr_dr_notes", label: __("Ignore System Generated Credit / Debit Notes"), fieldtype: "Check" },
    ],
};

// Add accounting dimensions
erpnext.utils.add_dimensions("Consolidated General Ledger", 15);
