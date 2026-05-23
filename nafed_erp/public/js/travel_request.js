frappe.ui.form.on("Travel Request", {
    employee: function(frm) {
        if (!frm.doc.employee) return;

        frappe.db.get_value("Employee", frm.doc.employee, "expense_approver")
            .then(r => {
                if (r && r.message && r.message.expense_approver) {
                    frm.set_value("custom_expense_approver", r.message.expense_approver);
                } else {
                    frm.set_value("custom_expense_approver", "");
                    frappe.msgprint("No Expense Approver set for this Employee.");
                }
            });
    },
    refresh(frm) {
        if (frm.doc.docstatus !== 1) return;

        // EMPLOYEE ADVANCE
        if (
            frm.doc.custom_payment_type === "Employee Advance" &&
            !frm.doc.custom_employee_advance &&
            frm.doc.custom_status === "Approved"
        ) {
            frm.add_custom_button(__("Create Employee Advance"), () => {
                frappe.call({
                    method: "nafed_erp.hire_to_retire.doc_events.travel_request.create_employee_advance_from_tr",
                    args: {
                        travel_request: frm.doc.name
                    },
                    callback(r) {
                        if (r.message) {
                            frappe.msgprint({
                                title: __("Employee Advance Created"),
                                message: __(
                                    "Employee Advance <b>{0}</b> has been successfully created for this Travel Request.",
                                    [r.message]
                                ),
                                indicator: "green"
                            });
        
                            frm.reload_doc();
                        }
                    }
                });
            });
        }
        

        // CREATE EXPENSE CLAIM (after Employee Advance exists)
        if (
            frm.doc.custom_payment_type === "Employee Advance" &&
            frm.doc.custom_employee_advance && frm.doc.custom_status==="Approved" && !frm.doc.custom_expense_claim
        ) {
            frm.add_custom_button(__("Create Expense Claim"), () => {
                frappe.call({
                    method: "nafed_erp.hire_to_retire.doc_events.travel_request.make_expense_claim_from_travel_request",
                    args: {
                        source_name: frm.doc.name
                    },
                    callback(r) {
                        if (r.message) {
                            frappe.model.sync(r.message);
                            frappe.set_route("Form", r.message.doctype, r.message.name);
                        }
                    }
                });
                
            });
        }
        // REIMBURSEMENT → EXPENSE CLAIM
        if (
            frm.doc.custom_payment_type === "Reimbursement" &&
            !frm.doc.custom_expense_claim && frm.doc.custom_status==="Approved"
        ) {
            frm.add_custom_button(__("Create Expense Claim"), () => {
                frappe.call({
                    method: "nafed_erp.hire_to_retire.doc_events.travel_request.make_expense_claim_from_travel_request",
                    args: {
                        source_name: frm.doc.name
                    },
                    callback(r) {
                        if (r.message) {
                            frappe.model.sync(r.message);
                            frappe.set_route("Form", r.message.doctype, r.message.name);
                        }
                    }
                });
                
            });
        }
    }
});

frappe.ui.form.on("Travel Itinerary", {
    departure_date(frm, cdt, cdn) {
        calculate_duration(frm, cdt, cdn);
    },

    arrival_date(frm, cdt, cdn) {
        calculate_duration(frm, cdt, cdn);
    }
});

function calculate_duration(frm, cdt, cdn) {
    let row = frappe.get_doc(cdt, cdn);

    if (row.departure_date && row.arrival_date) {
        let total_minutes = frappe.datetime.get_minute_diff(row.arrival_date, row.departure_date);

        let hours = Math.floor(total_minutes / 60);
        let minutes = total_minutes % 60;

        let formatted = `${hours}h ${minutes}m`;
        frappe.model.set_value(cdt, cdn, "custom_travel_duration", formatted);
    }
}


frappe.ui.form.on("Travel Request", {
    before_save: function(frm) {
        calculate_total_amount(frm);
    }
});

// ---------------------
// 2️⃣ Sum Total Amount of Costings Child Table
// ---------------------
function calculate_total_amount(frm) {
    let total = 0;

    (frm.doc.costings || []).forEach(row => {
        if (row.total_amount) {
            total += flt(row.total_amount);
        }
    });

    frm.set_value("custom_total_travel_amount", total);
}


frappe.ui.form.on("Travel Request", {
    before_save: function (frm) {
        let total_advance = 0;

        (frm.doc.itinerary || []).forEach(row => {
            total_advance += flt(row.advance_amount);
        });

        frm.set_value("custom_total_advance_amount", total_advance);
    }
});


frappe.ui.form.on("Travel Request Costing", {
    sponsored_amount: function (frm, cdt, cdn) {
        calculate_total(cdt, cdn);
    },

    funded_amount: function (frm, cdt, cdn) {
        calculate_total(cdt, cdn);
    }
});

function calculate_total(cdt, cdn) {
    let row = locals[cdt][cdn];

    let sponsored = row.sponsored_amount || 0;
    let funded = row.funded_amount || 0;

    row.total_amount = sponsored + funded;

    refresh_field("costings");
}


