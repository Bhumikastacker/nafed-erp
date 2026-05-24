frappe.ui.form.on("Expense Claim", {
    refresh(frm) {
        if (frm.doc.docstatus === 1) {

            frappe.call({
                method: "nafed_erp.hire_to_retire.doc_events.expense_claim.additional_salaries_status",
                args: { expense_claim: frm.doc.name },
                callback: function(r) {

                    const status = r.message;

                    // If ALL salaries are created → hide button
                    if (!status.all_created) {

                        frm.add_custom_button(
                            __("Additional Salaries"),
                            () => {
                                frappe.call({
                                    method: "nafed_erp.hire_to_retire.doc_events.expense_claim.create_additional_salaries",
                                    args: { expense_claim: frm.doc.name },
                                    callback: function(r) {
                                        frappe.msgprint(r.message);
                                        frm.reload_doc();
                                    }
                                });
                            },
                            __("Create")
                        );
                    }
                }
            });
        }
    }
});
