// Copyright (c) 2025, CSM Technologies Pvt Ltd and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Branch Payment Request", {
// 	refresh(frm) {

// 	},
// });
// Copyright (c) 2025, Aarti Kumari and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Branch Payment Request", {
// 	refresh(frm) {

// 	},
// });

frappe.ui.form.on("Branch Payment Request", {
    refresh(frm) {
        toggle_get_employee_button(frm);
        if (!frm.is_new() && frm.doc.docstatus === 1 && frm.doc.status === "Approved") {
            frm.add_custom_button("Fund Released Entry", function () {
                frappe.call({
                    method: "nafed_erp.hire_to_retire.doctype.branch_payment_request.branch_payment_request.create_payment_entry",
                    args: { docname: frm.doc.name },
                    callback: function (r) {
                        if (r.message) {
                            // Create a new unsaved Payment Entry document
                            let new_doc = frappe.model.sync(r.message)[0];

                            // Redirect user to the newly created Payment Entry
                            frappe.set_route("Form", "Payment Entry", new_doc.name);
                        }
                    }
                });
            }, "Create").addClass("btn-primary");
        }
        if (!frm.is_new() && frm.doc.docstatus === 1 && frm.doc.status === "Fund Released" && !frm.doc.fund_recevied_entry_id) {
            frm.add_custom_button("Fund Received", function () {
                frappe.call({
                    method: "nafed_erp.hire_to_retire.doctype.branch_payment_request.branch_payment_request.branch_payment_entry",
                    args: { docname: frm.doc.name },
                    callback: function (r) {
                        if (r.message) {
                            // Create a new unsaved Payment Entry document
                            let new_doc = frappe.model.sync(r.message)[0];

                            // Redirect user to the newly created Payment Entry
                            frappe.set_route("Form", "Payment Entry", new_doc.name);
                        }
                    }
                });
            }, "Create").addClass("btn-primary");
        }

        if (!frm.is_new() && frm.doc.docstatus === 1) {
            frm.add_custom_button("Resend Alert Email", function () {
                frappe.call({
                    method: "nafed_erp.hire_to_retire.doctype.branch_payment_request.branch_payment_request.resend_alert_email",
                    args: {
                        docname: frm.doc.name,
                    },
                    callback: function () {
                        frappe.msgprint("✅ Email alert resent successfully!");
                    },
                });
            }, "Create");
        }
    },
    onload: function(frm) {
        // 🔹 Limit allowed doctypes for 'reference_doctype'
        frm.set_query("reference_doctype", function() {
            return {
                filters: [
                    ["name", "in", ["Dunning", "Journal Entry", "Sales Invoice", "Sales Order"]]
                ]
            };
        });

        // 🔹 Filter 'reference_name' to show only submitted docs of selected doctype
        frm.set_query("reference_name", function() {
            if (frm.doc.reference_doctype) {
                return {
                    filters: {
                        docstatus: 1  // ✅ Only submitted docs
                    },
                    doctype: frm.doc.reference_doctype
                };
            }
        });
    },

    // Optional: Reset reference_name when reference_doctype changes
    reference_doctype: function(frm) {
        frm.set_value("reference_name", null);
    },
    transcation_type: function(frm){
        toggle_get_employee_button(frm);
    }
});

function toggle_get_employee_button(frm) {
    // Remove button first to avoid duplicates
    frm.remove_custom_button("Get Employees");

    // Add button only when NOT "Approval Requisition"
    if (frm.doc.docstatus !== 1 && frm.doc.transcation_type !== "Approval Requisition") {

        frm.add_custom_button("Get Employees", function () {
            frappe.call({
                method: "nafed_erp.hire_to_retire.doctype.branch_payment_request.branch_payment_request.get_employees",
                args: { doc: frm.doc },
                callback: function (r) {
                    if (r.message) {
                        frm.clear_table("employee_salary_details");

                        r.message.forEach(emp => {
                            let row = frm.add_child("employee_salary_details");
                            row.employee = emp.name;
                        });

                        frm.refresh_field("employee_salary_details");
                    }
                }
            });
        });
    }
}