frappe.ui.form.on('PF Trust Settings', {
    refresh(frm) {
        apply_account_filters(frm);
    },
    pf_trust_company(frm) {
        apply_account_filters(frm);
    }
});

function apply_account_filters(frm) {
    if (!frm.doc.pf_trust_company) return;

    // Posting accounts → LEDGER only
    const posting_filter = {
        filters: {
            company: frm.doc.pf_trust_company,
            is_group: 0,
            account_type :"Payable"
        }
    };

    frm.set_query('employee_pf_account_for_pf_trust', () => posting_filter);
    frm.set_query('employer_pf_account_for_pf_trust', () => posting_filter);
    frm.set_query('voluntary_pf_account_for_pf_trust', () => posting_filter);
}


frappe.ui.form.on("PF Trust Settings", {
    setup(frm) {
        frm.set_query("default_account", "default_account_mapping", function () {
            if (!frm.doc.pf_trust_company) {
                return {};
            }

            return {
                filters: {
                    company: frm.doc.pf_trust_company,
                    is_group: 0,
                    account_type :"Receivable"
                }
            };
        });
    }
});
