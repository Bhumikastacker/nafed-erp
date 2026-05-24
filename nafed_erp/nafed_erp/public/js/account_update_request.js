frappe.ui.form.on('Account Update Request', {
    onload_post_render(frm) {
        // Make fields editable after route_options are applied
        const fields = [
            'old_account_name',
            'old_account_number',
            'old_account_type',
            'old_parent_account',
            'old_company'
        ];

        fields.forEach(field => {
            frm.set_df_property(field, 'read_only', 1); // 0 = editable
        });
    }
});



frappe.ui.form.on("Account Update Request", {
    refresh(frm) {

        // Show Approve/Reject ONLY IF:
        // Submitted + Pending Approval + Admin Roles
        if (
            frm.doc.docstatus === 1 &&
            frm.doc.approval_status === "Pending Approval" &&
            (frappe.user.has_role("Administrator") || frappe.user.has_role("System Manager"))
        ) {
            // APPROVE BUTTON
            frm.add_custom_button("Approve", () => {
                frappe.confirm(
                    "Are you sure you want to approve this request?",
                    () => {
                        frappe.call({
                            method: "nafed_erp.hire_to_retire.doc_events.account_update.approve_request",
                            args: { docname: frm.doc.name },
                            callback: () => {
                                frappe.msgprint("Request Approved Successfully");
                                frm.reload_doc();
                            }
                        });
                    }
                );
            }, __("Actions"));

            // REJECT BUTTON
            frm.add_custom_button("Reject", () => {
                frappe.prompt(
                    [
                        {
                            fieldtype: "Small Text",
                            label: "Rejection Reason",
                            fieldname: "reason",
                            reqd: 1
                        }
                    ],
                    (values) => {
                        frappe.call({
                            method: "nafed_erp.hire_to_retire.doc_events.account_update.reject_request",
                            args: {
                                docname: frm.doc.name,
                                reason: values.reason
                            },
                            callback: () => {
                                frappe.msgprint("Request Rejected Successfully");
                                frm.reload_doc();
                            }
                        });
                    },
                    "Reject Request",
                    "Submit"
                );
            }, __("Actions"));
        }
    },

    // Auto-fill employee details
    onload(frm) {
        if (!frm.doc.requested_by) {
            frm.set_value("requested_by", frappe.session.user);
        }

        if (!frm.doc.request_date) {
            frm.set_value("request_date", frappe.datetime.get_today());
        }
    }
});
