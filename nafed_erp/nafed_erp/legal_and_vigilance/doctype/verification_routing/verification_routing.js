// Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on("Verification Routing", {
	refresh(frm) {
        // Show button only if doc is saved
        if (!frm.is_new()) {
            frm.add_custom_button(
                __("Create Verification Reporting"),
                function () {
                    frappe.call({
                        method: "nafed_erp.legal_and_vigilance.doctype.verification_routing.verification_routing.create_verification_reporting",
                        args: {
                            verification_routing_id: frm.doc.name
                        },
                        callback: function (r) {
                            if (r.message) {
                                frappe.msgprint("Verification Reporting Created");
                                frappe.set_route("Form", "Verification Reporting", r.message);
                            }
                        }
                    });
                },
                __("Actions")
            );
        }
    }
});

