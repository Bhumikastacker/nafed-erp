// Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Field Inspection Report", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on('Field Inspection Report', {
    onload: function(frm) {

        // Set filter for value field inside child table
        frm.fields_dict.general_observations.grid.get_field('value').get_query = function(doc, cdt, cdn) {
            let row = locals[cdt][cdn];

            return {
                filters: {
                    parameter: row.parameter
                }
            };
        };
    }
});
frappe.ui.form.on('Field Inspection Report', {
    refresh: function(frm) {
        if (!frm.doc.general_observations.length) {

            let parameters = [
                "Level of germination in field",
                "Level of plant stand / crop growth",
                "Level of off-type admixture",
                "Damage due to pests/diseases",
                "Standard agronomic practices",
                "Crop/Variety of nearby fields"
            ];

            parameters.forEach(param => {
                let row = frm.add_child('general_observations');
                row.parameter = param;
            });

            frm.refresh_field('general_observations');
        }
    }
});