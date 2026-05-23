frappe.ui.form.on('Account', {
    refresh(frm) {
        frm.add_custom_button(__('Request Update'), () => {

            // Pass values to the next form
            frappe.route_options = {
                old_account_name: frm.doc.account_name,
                old_account_number: frm.doc.account_number,
                old_account_type: frm.doc.account_type,
                old_parent_account: frm.doc.parent_account,
                old_company: frm.doc.company,
                requested_by:frappe.session.user,
                request_date:frappe.datetime.get_today()
            };

            // Redirect to new Account Update Request
            frappe.set_route('Form', 'Account Update Request', 'new');
        });
    }
});

frappe.ui.form.on("Account", {
    onload(frm) {
        if (!frm.is_new()) {
            frm._original_parent_account = frm.doc.parent_account;
        }
    },

    refresh(frm) {
        if (!frm.is_new() && !frm._original_parent_account) {
            frm._original_parent_account = frm.doc.parent_account;
        }
    },

    async parent_account(frm) {
        if (frm.is_new()) return;

        const old_parent = frm._original_parent_account;
        const new_parent = frm.doc.parent_account;

        if (old_parent === new_parent) return;

        const r = await frappe.call({
            method: "nafed_erp.finance_and_accounts.doc_events.account.account_has_balance",
            args: { account: frm.doc.name }
        });

        if (!r.message) {
            frm._original_parent_account = new_parent;
            return;
        }

        frappe.prompt(
            [
                {
                    label: `This account has balance. Do you want to change the parent account?`,
                    fieldname: "confirm",
                    fieldtype: "Select",
                    options: ["No", "Yes"],
                    default: "No"
                }
            ],
            async (data) => {
                if (data.confirm === "No") {
                    frappe.show_alert("Reverted parent account.");
                    frm.set_value("parent_account", old_parent);
                } else {
                    frm._original_parent_account = new_parent;

                    // 🔥🔥 Automatically Save When User Selects YES
                    await frm.save();
                }
            },
            "Confirm Parent Change",
            "Submit"
        );
    }
});
