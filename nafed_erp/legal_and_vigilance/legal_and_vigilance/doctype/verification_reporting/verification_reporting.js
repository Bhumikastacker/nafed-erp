// Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on("Verification Reporting", {
	refresh(frm) {
        if (!frm.is_new()) {
            frm.add_custom_button(
                __("Create Memo Issuance"),
                function () {
                    frappe.call({
                        method: "nafed_erp.legal_and_vigilance.doctype.verification_reporting.verification_reporting.create_memo_issuance",
                        args: {
                            verification_reporting_id: frm.doc.name
                        },
                        callback: function (r) {
                            if (r.message) {
                                frappe.msgprint("Memo Issuance Created");
                                frappe.set_route("Form", "Memo Issuance", r.message);
                            }
                        }
                    });
                },
                __("Actions")
            );
        }
    }
});


