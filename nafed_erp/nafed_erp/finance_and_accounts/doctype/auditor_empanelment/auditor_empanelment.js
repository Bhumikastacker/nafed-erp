// Copyright (c) 2026

frappe.ui.form.on("Auditor Empanelment", {

    // ✅ Filter Rate Card based on Auditor Type
    auditor_type(frm) {
        if (frm.doc.auditor_type) {

            // Parent field filter
            frm.set_query("auditor_rate_card", function () {
                return {
                    filters: {
                        auditor_type: frm.doc.auditor_type
                    }
                };
            });

            // Child table filter
            frm.set_query("auditor_rate_card", "add_others_auditor_empanelment", function () {
                return {
                    filters: {
                        auditor_type: frm.doc.auditor_type
                    }
                };
            });
        }
    },

    // ✅ On Submit → Create Supplier
    on_submit: function(frm) {

        if (frm.doc.is_supplier) {

            // 🔒 Check if already created
            frappe.call({
                method: "frappe.client.get_list",
                args: {
                    doctype: "Supplier",
                    filters: {
                        custom_auditor_empanelment: frm.doc.name
                    },
                    fields: ["name"],
                    limit_page_length: 1
                },
                callback: function(res) {

                    if (res.message && res.message.length > 0) {
                        frappe.msgprint("Supplier already exists");
                        return;
                    }

                    // ✅ Create Supplier
                    let supplier_doc = {
                        doctype: "Supplier",
                        supplier_name: frm.doc.auditor_name,
                        supplier_group: frm.doc.auditor_type,
                        pan: frm.doc.pan_no,
                        gstin: frm.doc.registration_no,
                        supplier_type: "Individual",
                        custom_other: 1,
                        custom_auditor_empanelment: frm.doc.name
                    };

                    frappe.call({
                        method: "frappe.client.insert",
                        args: {
                            doc: supplier_doc
                        },
                        callback: function(r) {
                            if (r.message) {
                                frappe.msgprint("✅ Supplier Created: " + r.message.name);
                            }
                        }
                    });

                }
            });
        }
    },

    // ✅ Refresh → Create Audit Assignment Button
    refresh: function(frm) {

        if (frm.doc.docstatus === 1) {

            frappe.call({
                method: "frappe.client.get_list",
                args: {
                    doctype: "Audit Assignment",
                    filters: {
                        auditor: frm.doc.name
                    },
                    fields: ["name"],
                    limit_page_length: 1
                },
                callback: function(r) {

                    // ❌ Already exists → do nothing
                    if (r.message && r.message.length > 0) {
                        return;
                    }

                    // ✅ Add button
                    frm.add_custom_button("Create Audit Assignment", function() {

                        let doc = frappe.model.get_new_doc("Audit Assignment");

                        doc.auditor = frm.doc.name;

                        frappe.set_route("Form", "Audit Assignment", doc.name);
                    });
                }
            });
        }
    }
});