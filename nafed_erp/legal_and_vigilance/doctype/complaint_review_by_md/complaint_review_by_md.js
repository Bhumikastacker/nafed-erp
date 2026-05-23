// Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Complaint Review by MD", {
// 	refresh(frm) {

// 	},
// });


frappe.ui.form.on("Complaint Review by MD", {
    refresh(frm) {
        // Show button only if doc is saved
        if (!frm.is_new()) {
            frm.add_custom_button(
                __("Create Verification Routing"),
                function () {
                    frappe.call({
                        method: "nafed_erp.legal_and_vigilance.doctype.complaint_review_by_md.complaint_review_by_md.create_verification_routing",
                        args: {
                            complaint_review_id: frm.doc.name
                        },
                        callback: function (r) {
                            if (r.message) {
                                frappe.msgprint("Verification Routing Created");
                                frappe.set_route("Form", "Verification Routing", r.message);
                            }
                        }
                    });
                },
                __("Actions")
            );
        }
    }
});
