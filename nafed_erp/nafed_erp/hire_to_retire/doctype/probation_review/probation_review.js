// Copyright (c) 2025, CSM Technologies Pvt Ltd and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Probation Review", {
// 	refresh(frm) {

// 	},
// });

frappe.ui.form.on("Probation Review", {
    probhation_checklist_template(frm){
        if(!frm.doc.probhation_checklist_template){
            frm.clear_table("probation_review");
            frm.refresh_field("probation_review");
            return;
        }
        frappe.db.get_doc("Probation Checklist Template", frm.doc.probhation_checklist_template)
        .then(template_doc => {
            frm.clear_table("probation_review");
            (template_doc.probation_review || []).forEach(row => {
                let new_row = frm.add_child("probation_review",{
                    review_checklist: row.review_checklist,
                    performance_rating: row.performance_rating
                }) ;               
            });
            frm.refresh_field("probation_review")
        })
    }
})