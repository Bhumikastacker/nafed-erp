// Copyright (c) 2025, CSM Technologies Pvt Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on("Law Code", {
 	onload: function(frm) {
        if (frm.is_new()) {
            frm.set_value('active', 1);
        }
    }
 });
