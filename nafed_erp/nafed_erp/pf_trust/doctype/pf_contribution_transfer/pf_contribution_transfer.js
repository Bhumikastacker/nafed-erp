frappe.ui.form.on('PF Contribution Transfer', {
    onload(frm){
        set_pf_trust_company(frm, true);
    },  
    refresh(frm) {
        toggle_fetch_button(frm);
        toggle_post_submit_buttons(frm);
        set_pf_trust_company(frm, false);
    }
});

function toggle_fetch_button(frm) {
    // Remove first to avoid duplicates
    frm.remove_custom_button(__('Fetch Salary Slips'));

    // Conditions to show button
    const is_draft = frm.doc.docstatus === 0;
    const is_not_new = !frm.is_new();
    const has_rows = frm.doc.pf_contribution
        && frm.doc.pf_contribution.length > 0;

    // Show button ONLY if:
    // - Draft
    // - Saved
    // - Child table empty
    if (is_draft && is_not_new && !has_rows) {
        frm.add_custom_button(__('Fetch Salary Slips'), () => {
            fetch_salary_slips(frm);
        });
    }
}

function fetch_salary_slips(frm) {
    frappe.call({
        method: "nafed_erp.pf_trust.doctype.pf_contribution_transfer.pf_contribution_transfer.fetch_salary_slips",
        args: {
            docname: frm.doc.name
        },
        freeze: true,
        freeze_message: __("Fetching salary slips…")
    }).then(() => {
        frm.reload_doc();
    });
}

function toggle_post_submit_buttons(frm) {
    // Clean slate
    frm.remove_custom_button(__('Create Journal Entry'));

    // Only after submit
    if (frm.doc.docstatus === 1) {

        // If JE not created yet
        if (!frm.doc.journal_entry) {
            frm.add_custom_button(__('Create Journal Entry'), () => {
                create_pf_journal_entry(frm);
            }, __('Actions'));
        } 
    }
}

function create_pf_journal_entry(frm) {
    frappe.call({
        method: "nafed_erp.pf_trust.doctype.pf_contribution_transfer.pf_contribution_transfer.create_journal_entry",
        args: {
            docname: frm.doc.name
        },
        freeze: true,
        freeze_message: __("Creating PF Journal Entry…")
    }).then((r) => {

        if (r.message) {
            frappe.msgprint({
                title: __("Success"),
                indicator: "green",
                message: __("Journal Entry <b>{0}</b> created successfully.", [r.message])
            });
        }

        frm.reload_doc();
    });
}


function set_pf_trust_company(frm, set_default) {
    frappe.call({
        method: "nafed_erp.pf_trust.doctype.pf_contribution_transfer.pf_contribution_transfer.get_pf_trust_company",
        callback: function (r) {
            if (!r.message) return;

            // 1️⃣ Restrict query
            frm.set_query("pf_trust_company", () => {
                return {
                    filters: { name: r.message }
                };
            });

            // 2️⃣ Set default ONLY on load & if empty
            if (set_default && !frm.doc.pf_trust_company) {
                frm.set_value("pf_trust_company", r.message);
            }
        }
    });
}