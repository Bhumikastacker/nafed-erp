// frappe.ui.form.on("Leave Encashment", {
//     employee: function(frm) {

//         frappe.call({
//             method: "frappe.client.get_list",
//             args: {
//                 doctype: "Salary Structure Assignment",
//                 filters: {
//                     employee: frm.doc.employee,
//                     docstatus: 1
//                 },
//                 fields: ["name", "base"],
//                 order_by: "from_date desc",
//                 limit_page_length: 1
//             },
//             callback(r) {
//                 if (!r.message || !r.message.length) {
//                     frappe.msgprint("No Salary Structure Assignment found.");
//                     return;
//                 }

//                 frm.set_value("custom_salary_structure_assignment", r.message[0].name);  
//             }
//         });
//     }
// });
frappe.ui.form.on("Leave Encashment", {

    refresh: function(frm) {
        frm.__auto_setting = false;
    },

    leave_type: function(frm) {
        if (!frm.doc.leave_type) return;

        frm.__auto_setting = true;

        frappe.db.get_value(
            'Leave Type',
            frm.doc.leave_type,
            'max_encashable_leaves'
        ).then(r => {

            let master_days = r.message.max_encashable_leaves || 0;

            frm.set_value('encashment_days', master_days);

            frm.__auto_setting = false;
        });
    },

    encashment_days: function(frm) {

        // Skip if auto setting
        if (frm.__auto_setting) return;

        if (!frm.doc.leave_type) return;

        let input_days = frm.doc.encashment_days;

        if (input_days === undefined || input_days === null) return;

        // ✅ Zero / Negative Check
        if (input_days <= 0) {

            frappe.msgprint({
                title: __('Invalid Value'),
                indicator: 'red',
                message: __('Encashment days cannot be zero or negative. Resetting to minimum 1 day.')
            });

            frm.set_value('encashment_days', 1);
            return;
        }

        // ✅ Strict Max Limit Check
        frappe.db.get_value(
            'Leave Type',
            frm.doc.leave_type,
            'max_encashable_leaves'
        ).then(r => {

            let max_limit = r.message.max_encashable_leaves || 0;

            if (input_days > max_limit) {

                frappe.msgprint({
                    title: __('Limit Exceeded'),
                    indicator: 'orange',
                    message: __(
                        'Maximum allowed days for <b>{0}</b> is <b>{1}</b>.',
                        [frm.doc.leave_type, max_limit]
                    )
                });

                frm.set_value('encashment_days', max_limit);
            }
        });
    }

});


frappe.ui.form.on("Leave Encashment Component", {
    salary_component(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);

        if (!frm.doc.employee) {
            frappe.msgprint("Select employee first.");
            return;
        }

        frappe.call({
            method: "nafed_erp.hire_to_retire.doc_events.leave_encashment.get_component_amount",
            args: {
                employee: frm.doc.employee,
                salary_component: row.salary_component
            },
            callback(r) {
                let amount = r.message.amount || 0;
                row.amount = amount;

                frm.refresh_field("custom_salary_component");
                frm.trigger("calculate_total_amount");
            }
        });
    }
});


frappe.ui.form.on("Leave Encashment", {
    employee(frm) {
        set_salary_component_filter(frm);
    },
    refresh(frm) {
        set_salary_component_filter(frm);
    }
});

function set_salary_component_filter(frm) {
    frm.set_query("salary_component", "custom_salary_component", function() {
        return {
            query: "nafed_erp.hire_to_retire.doc_events.leave_encashment.get_earnings_salary_components",
            filters: {
                employee: frm.doc.employee
            }
        };
    });
}
