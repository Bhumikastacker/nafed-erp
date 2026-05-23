// Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Incidental Charges", {
// 	refresh(frm) {

// 	},
// });


frappe.ui.form.on("Incidental Charges", {

    qty: function(frm) {
        calculate_amount(frm);
    },

    rate: function(frm) {
        calculate_amount(frm);
    }
});

function calculate_amount(frm) {
    let qty = frm.doc.qty || 0;
    let rate = frm.doc.rate || 0;

    let amount = qty * rate;

    frm.set_value("amount", amount);
}
