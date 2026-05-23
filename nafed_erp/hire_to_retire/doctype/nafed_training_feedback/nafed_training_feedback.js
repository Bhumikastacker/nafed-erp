// Copyright (c) 2025, CSM Technologies Pvt Ltd and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Nafed Training Feedback", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on("Nafed Training Feedback", {
    rating: function(frm) {
        if (frm.doc.rating) {
            let stars = frm.doc.rating * 5;      // convert 0–1 scale to 1–5 stars
            frm.set_value("rating_score", stars);
        } else {
            frm.set_value("rating_score", 0);
        }
    },
    refresh(frm){
        if (!frm.doc.employee_skill_map && frm.doc.feedback_type !="Trainer") {

            frm.add_custom_button("Update Employee Skill", function () {

                frappe.model.with_doctype("Employee Skill Map", () => {
                    let lp = frappe.model.get_new_doc("Employee Skill Map");

                    lp.custom_employee_feedback_id = frm.doc.name;
                    lp.custom_meeting_id = frm.doc.meeting;
                    lp.employee = frm.doc.employee;
                    lp.custom_evaluation_type = frm.doc.feedback_type;
                    frappe.set_route("Form", "Employee Skill Map", lp.name);
                });

            });
        }
    }
});

