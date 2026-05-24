// Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on('Supplier Payment', {

    amount_paid: function(frm) {
        calculate_balance(frm);
    }

});

function calculate_balance(frm) {

    let total = frm.doc.total_payable || 0;
    let paid = frm.doc.amount_paid || 0;

    let balance = total - paid;

    frm.set_value("balance_amount", balance);

    // Auto status
    if (paid === 0) {
        frm.set_value("status", "Draft");
    } else if (balance > 0) {
        frm.set_value("status", "Partially Paid");
    } else {
        frm.set_value("status", "Paid");
    }
}