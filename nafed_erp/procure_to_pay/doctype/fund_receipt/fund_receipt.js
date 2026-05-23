// Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on('Fund Receipt', {

    refresh: function(frm) {

        if (!frm.is_new()) {

            frm.add_custom_button('Distribute Subsidy', function() {

                frappe.model.with_doctype('Subsidy Distribution', function() {

                    let doc = frappe.model.get_new_doc('Subsidy Distribution');

                    doc.subsidy_request = frm.doc.subsidy_request;
                    doc.total_amount = frm.doc.received_amount;
                    doc.balance_amount = frm.doc.received_amount;

                    frappe.set_route('Form', 'Subsidy Distribution', doc.name);

                });

            }, 'Create');
        }
    }
});