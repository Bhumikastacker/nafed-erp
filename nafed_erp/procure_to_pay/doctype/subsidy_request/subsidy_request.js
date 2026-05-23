// Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on('Subsidy Request', {

    refresh: function(frm) {

        if (!frm.is_new()) {

            frm.add_custom_button('Create Fund Receipt', function() {

                if (!frm.doc.total_amount) {
                    frappe.msgprint("Total Amount is missing");
                    return;
                }

                frappe.model.with_doctype('Fund Receipt', function() {

                    let doc = frappe.model.get_new_doc('Fund Receipt');

                    doc.subsidy_request = frm.doc.name;
                    doc.received_amount = frm.doc.total_amount;
                    doc.receipt_date = frappe.datetime.nowdate();

                    doc.status = "Received";

                    frappe.set_route('Form', 'Fund Receipt', doc.name);

                });

            }, 'Create');
        }
    }
});