// Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
// For license information, please see license.txt


frappe.ui.form.on("Tender Management", {
    refresh: function(frm) {

        // ✅ Base condition
        if (frm.doc.docstatus === 1 && frm.doc.feedback_status === "Accept") {

            // 🔍 Check if Auditor Empanelment already exists
            frappe.db.get_list("Auditor Empanelment", {
                filters: {
                    ref: frm.doc.name   // 👈 your link field
                },
                limit: 1
            }).then((res) => {

               
                if (res && res.length > 0) {
                    return;
                }

                
                frm.add_custom_button("Create Auditor Empanelment", function () {

                    frappe.msgprint("Auditor Empanelment Create Button Clicked");

                    frappe.new_doc("Auditor Empanelment", {
                        ref: frm.doc.name
                    });

                }, "Create");

            });
        }
    }
});