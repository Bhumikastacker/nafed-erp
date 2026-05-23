// Copyright (c) 2025, CSM Technologies Pvt Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on("Leave Encashment Request", {
    refresh(frm) {
        frm.set_query("leave_type", () => {
            return {
                filters: {
                    // leave types that have allocation for this employee
                    name: [
                        "in",
                        (
                            frm.doc.employee
                            ? get_allocated_leave_types(frm.doc.employee)
                            : []
                        )
                    ],
                    is_earned_leave: 1,
                    allow_encashment: 1
                }
            };
        });
    }
});

/**
 * Fetch Leave Types allocated to employee using frappe.call
 *
 * Synchronous call wrapped inside a promise to avoid UI delay
 */
function get_allocated_leave_types(employee) {
    let allocated = [];

    frappe.call({
        method: "frappe.client.get_list",
        async: false,
        args: {
            doctype: "Leave Allocation",
            fields: ["leave_type"],
            filters: {
                employee: employee,
                docstatus: 1
            }
        },
        callback(r) {
            if (r.message) {
                allocated = r.message.map(d => d.leave_type);
            }
        }
    });

    return allocated;
}


frappe.ui.form.on("Leave Encashment Request", {
    leave_type(frm) {
        if (!frm.doc.employee || !frm.doc.leave_type) return;

        frappe.call({
            method: "nafed_erp.hire_to_retire.doc_events.leave_encashment.get_leave_balance",
            args: {
                employee: frm.doc.employee,
                leave_type: frm.doc.leave_type
            },
            callback(r) {
                if (r.message !== undefined) {
                    frm.set_value("available_balance", r.message);
                }
            }
        });
    }
});



frappe.ui.form.on("Leave Encashment Request", {
    employee: function(frm) {
        if (!frm.doc.employee) return;

        frm.clear_table("leave_encashment_request_approvers");

        frappe.call({
            method: "nafed_erp.hire_to_retire.doctype.leave_encashment_request.leave_encashment_request.get_leave_encashment_approvers",
            args: {
                employee: frm.doc.employee
            },
            callback: function(r) {

                // If no approvers configured
                if (!r.message || r.message.length === 0) {

                    frappe.msgprint({
                        title: __("No Leave Approver Found"),
                        indicator: "orange",
                        message: __(
                            "No leave encashment approver is configured for this employee. " +
                            "Please contact HR to configure approvers."
                        )
                    });

                    frm.refresh_field("leave_encashment_request_approvers");
                    return;
                }

                // Populate approvers
                r.message.forEach(row => {
                    let child = frm.add_child("leave_encashment_request_approvers");
                    child.request_approver_user_id = row.request_approver_user_id;
                    child.request_approver_name = row.request_approver_name;
                });

                frm.refresh_field("leave_encashment_request_approvers");
            }
        });
    }
});


frappe.ui.form.on("Leave Encashment Request", {
    refresh(frm) {

        // condition you already had
        if (frm.doc.docstatus !== 1 || frm.doc.status !== "Approved") {
            return;
        }

        if (!frm.doc.leave_encashment_request_approvers) return;

        const current_user = frappe.session.user;

        const is_approver = frm.doc.leave_encashment_request_approvers.some(
            row => row.request_approver_user_id === current_user
        );

        // ❌ not an approver → no button
        if (!is_approver) return;

        // ✅ approver → show button
        frm.add_custom_button("Create Encashment", () => {
            frappe.model.open_mapped_doc({
                method: "nafed_erp.hire_to_retire.doctype.leave_encashment_request.leave_encashment_request.create_encashment",
                frm: frm
            });
        }, "Actions");
    }
});


frappe.ui.form.on("Leave Encashment Request", {
    refresh(frm) {

        // remove buttons first (important on refresh)
        frm.remove_custom_button("Approve", "Actions");
        frm.remove_custom_button("Reject", "Actions");

        if (
            frm.doc.docstatus !== 1 ||
            ["Approved", "Rejected"].includes(frm.doc.status)
        ) {
            return;
        }

        if (!frm.doc.leave_encashment_request_approvers) return;

        const current_user = frappe.session.user;

        const is_approver = frm.doc.leave_encashment_request_approvers.some(
            row => row.request_approver_user_id === current_user
        );

        if (!is_approver) return;

        // UI label + stored value separation
        add_action_button(frm, "Approve", "Approved");
        add_action_button(frm, "Reject", "Rejected");
    }
});

function add_action_button(frm, label, status_value) {
    frm.add_custom_button(label, () => {
        frappe.confirm(
            `Do you want to ${label.toLowerCase()}?`,
            () => {
                frappe.call({
                    method:
                        "nafed_erp.hire_to_retire.doctype.leave_encashment_request.leave_encashment_request.update_status_and_notify",
                    args: {
                        name: frm.doc.name,
                        status: status_value   // ✅ DB value
                    },
                    callback() {
                        frappe.msgprint(`Request ${status_value}`);
                        frm.reload_doc();
                    }
                });
            }
        );
    }, __("Actions"));
}