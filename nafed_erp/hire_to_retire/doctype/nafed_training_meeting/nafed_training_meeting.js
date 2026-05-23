// Copyright (c) 2025, CSM Technologies Pvt Ltd and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Nafed Training Meeting", {
// 	refresh(frm) {

// 	},
// });
// frappe.ui.form.on('Nafed Training Meeting', {
//     refresh: function(frm) {
//         frm.add_custom_button(__('Mark Attendance'), function() {
//             frappe.call({
//                  method: "nafed_erp.hire_to_retire.doctype.nafed_training_meeting.nafed_training_meeting.mark_training_attendance",
//                 args: { docname: frm.doc.name },
//                 callback: function(r) {
//                     frappe.msgprint(r.message || r);
//                     frm.reload_doc();
//                 }
//             });
//         });
//     }
// });


frappe.ui.form.on('Nafed Training Meeting', {
    refresh: function(frm) {

        // Show only after submit
        frm.fields_dict["attendees"].grid.refresh();

        if (frm.doc.docstatus === 1) {

            frm.add_custom_button(__('Mark Attendance'), function() {

                frappe.call({
                    method: "nafed_erp.hire_to_retire.doctype.nafed_training_meeting.nafed_training_meeting.mark_training_attendance",
                    args: { docname: frm.doc.name },
                    callback: function(r) {
                        frappe.msgprint(r.message || r);
                        frm.reload_doc();
                    }
                });

            }); 
        }
        frm.set_query('custom_attendance', function() {
            return {
                filters: {
                    name: ['in', ['Branch', 'Designation', 'Department']]
                }
            };
        });
    },
   custom_attendance: function(frm) {
        // Clear custom_id when attendance changes
        frm.set_value('custom_id', '');
        frm.clear_table('attendees');
        frm.refresh_field('attendees');
    },

    custom_id: async function(frm) {
        // Run only if both fields are selected
        if (!frm.doc.custom_attendance || !frm.doc.custom_id) return;

        // Clear existing attendees
        frm.clear_table('attendees');

        // Build filters based on custom_attendance
        let filters = {};
        const attendance = frm.doc.custom_attendance;
        const custom_value = frm.doc.custom_id;

        if (attendance === 'Branch') filters['branch'] = custom_value;
        else if (attendance === 'Department') filters['department'] = custom_value;
        else if (attendance === 'Designation') filters['designation'] = custom_value;

        // Fetch employees from Employee master
        let employees = await frappe.db.get_list('Employee', {
            filters: filters,
            fields: ['name','employee_name']
        });

        // Add employees to attendees child table
        employees.forEach(emp => {
            let row = frm.add_child('attendees');
            row.employee = emp.name;
            row.employee_name = emp.employee_name;
            //  row.personal_email = emp.email;
        });

        frm.refresh_field('attendees');
    }

});

frappe.ui.form.on("Nafed Training Meeting", {
    refresh(frm) {
        if (frm.doc.docstatus === 1) {
            frm.add_custom_button("Send Feedback", () => {
                frappe.call({
                    method: "nafed_erp.hire_to_retire.doctype.nafed_training_meeting.nafed_training_meeting.send_feedback_to_all_attendees",
                    args: { meeting: frm.doc.name },
                    callback(r) {
                        frappe.msgprint("Feedback Email Sent Successfully");
                    }
                });
            });
        }
    }
});

frappe.ui.form.on('Nafed Training Meeting', {
    refresh(frm) {

        // Remove buttons if workflow is Rejected
        if (frm.doc.workflow_state === "Rejected") {
            frm.remove_custom_button("Mark Attendance");
            frm.remove_custom_button("Send Feedback");
            return;
        }

        // Otherwise add buttons normally (if you already have logic)
        if (!frm.is_new()) {
            frm.add_custom_button("Mark Attendance", () => {
                // your existing code
            });

            frm.add_custom_button("Send Feedback", () => {
                // your existing code
            });
        }
    }
});


// frappe.ui.form.on('Nafed Training Meeting', {
//     refresh: function(frm) {
//         // Find the current employee in the attendees table
//         let employee_att = frm.doc.attendees.find(att => att.employee === frappe.session.user);

//         // Show Leave Meeting button only if join_time is set
//         if (employee_att && employee_att.join_time && !employee_att.leave_time) {
//             frm.add_custom_button(__('Leave Meeting'), function() {
//                 frappe.call({
//                     method: "nafed_erp.api.leave_meeting",
//                     args: {
//                         meeting: frm.doc.name,
//                         emp: frappe.session.user
//                     },
//                     callback: function(r) {
//                         // redirection handled by API
//                     }
//                 });
//             });
//         }
//     }
// });



