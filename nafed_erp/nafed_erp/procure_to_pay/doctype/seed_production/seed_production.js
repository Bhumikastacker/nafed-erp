// Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on('Seed Production', {
    refresh: function(frm) {
        if (!frm.is_new()) {
            frm.add_custom_button('Create Subsidy Claim', function() {
                create_claim(frm);
            }, 'Create');
        }
    }
});
function create_claim(frm) {

    frappe.model.with_doctype('Subsidy Claim', function() {

        let doc = frappe.model.get_new_doc('Subsidy Claim');

        doc.supplier = frm.doc.supplier;
        doc.seed_production = frm.doc.name;
        doc.claim_date = frappe.datetime.nowdate();

        // 🔥 pass values
        doc.produced_quantity = frm.doc.produced_quantity || 0;
        doc.eligible_quantity = frm.doc.accepted_quantity || 0;

        frappe.set_route('Form', 'Subsidy Claim', doc.name);
    });
}
frappe.ui.form.on('Subsidy Claim', {

    subsidy_rate: function(frm) {
        calculate_claim(frm);
    },

    eligible_quantity: function(frm) {
        calculate_claim(frm);
    }
});

function calculate_claim(frm) {

    let qty = frm.doc.eligible_quantity || 0;
    let rate = frm.doc.subsidy_rate || 0;

    frm.set_value('claim_amount', qty * rate);
}