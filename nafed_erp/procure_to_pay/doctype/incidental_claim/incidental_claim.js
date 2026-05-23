// Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Incidental Claim", {
// 	refresh(frm) {

// 	},
// });

frappe.ui.form.on('Incidental Claim', {

    items_add: function(frm) {
        frm.trigger("calculate");
    },

    calculate: function(frm) {
        frm.refresh_field("items");
    }
});
