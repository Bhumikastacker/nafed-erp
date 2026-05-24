frappe.ui.form.on("Company", {
    refresh(frm) {
        set_custom_closing_account_filter(frm);
    }
});

function set_custom_closing_account_filter(frm) {
    frm.set_query("custom_closing_account", function() {
        return {
            filters: [
                ["Account", "company", "=", frm.doc.name],
                ["Account", "is_group", "=", "0"],
                ["Account", "freeze_account", "=", "No"],
                ["Account", "root_type", "in", "Liability, Equity"],
            ],
        };
    });
}


frappe.ui.form.on("Company", {
    setup(frm) {
        frm.set_query("custom_default_payment_account", function() {
            return {
                filters: {
                    company: frm.doc.name,
                    is_group: 0,
                    account_type: ["in", ["Bank", "Cash"]]
                }
            };
        });
    }
});
