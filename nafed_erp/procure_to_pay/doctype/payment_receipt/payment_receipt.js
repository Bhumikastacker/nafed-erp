// Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
// For license information, please see license.txt


frappe.ui.form.on('Payment Receipt', {

    amount_received: function(frm) {
        calculate_receipt(frm);
    }

});

function calculate_receipt(frm) {

    let total = frm.doc.total_receivable || 0;
    let received = frm.doc.amount_received || 0;

    let balance = total - received;

    frm.set_value("balance", balance);

    if (received === 0) {
        frm.set_value("status", "Draft");
    } else if (balance > 0) {
        frm.set_value("status", "Partially Received");
    } else {
        frm.set_value("status", "Received");
    }
}

frappe.ui.form.on('Payment Receipt', {

    refresh: function(frm) {

        if (!frm.is_new() && frm.doc.status === "Received") {

            frm.add_custom_button('Create Subsidy Claim', function() {

                frappe.model.with_doctype('Subsidy Claim', function() {

                    let doc = frappe.model.get_new_doc('Subsidy Claim');

                    doc.supplier = frm.doc.supplier;
                    doc.payment_receipt = frm.doc.name;
                    doc.lot_id = frm.doc.lot_id;

                    frappe.set_route('Form', 'Subsidy Claim', doc.name);

                });

            }, 'Create');

        }
    }

});