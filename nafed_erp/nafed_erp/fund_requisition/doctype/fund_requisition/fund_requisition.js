// Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Fund Requisition", {
// 	refresh(frm) {

// 	},
// });

frappe.ui.form.on("Fund Requisition", {
    refresh(frm) {
        // Show the button only after the document is saved (status becomes Draft)
        if (!frm.is_new()) {
            frm.add_custom_button(__('Payment'), function() {
                // Open a new Payment Entry and map fields from Fund Requisition
                frappe.new_doc("Payment Entry", {
                    payment_type: "Pay",
                    party_type: "Supplier",
                    
                    // Mapping amount from Fund Requisition to Payment Entry
                    paid_amount: frm.doc.amount_rs, 
                    received_amount: frm.doc.amount_rs,
                    
                    // Passing the document name as reference
                    reference_no: frm.doc.name,
                    reference_date: frm.doc.request_date,
                    
                    // Mapping the party name and company
                    party: frm.doc.name_of_the_party,
                    company: frm.doc.requested_branch
                });
            });
        }
    }
});