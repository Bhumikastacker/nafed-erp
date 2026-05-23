frappe.ui.form.on("Investment", {
    onload: function(frm) {
        set_account_query(frm);
    },
    company: function(frm) {
        set_account_query(frm);
    }
});

function set_account_query(frm) {
    frm.set_query("investment_account", function() {
        if (!frm.doc.company) {
            frappe.msgprint("Please select Company first");
            return;
        }

        return {
            filters: {
                company: frm.doc.company,
                is_group : 0
            }
        };
    });
}