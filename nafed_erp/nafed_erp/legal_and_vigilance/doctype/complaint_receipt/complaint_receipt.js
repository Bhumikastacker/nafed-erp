// Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Complaint Receipt", {
// 	refresh(frm) {

// 	},
// });

frappe.ui.form.on("Complaint Receipt", {
    refresh: function (frm) {
        // Show button only after submit
        if (frm.doc.docstatus === 1) {
            frm.add_custom_button(
                __("Review by MD"),
                function () {
                    frappe.call({
                        method: "nafed_erp.legal_and_vigilance.doctype.complaint_receipt.complaint_receipt.create_md_review",
                        args: {
                            complaint_id: frm.doc.name
                        },
                        callback: function (r) {
                            if (r.message) {
                                frappe.set_route("Form", "Complaint Review by MD", r.message);
                            }
                        }
                    });
                },
                __("Actions")
            );
        }
    }
});
