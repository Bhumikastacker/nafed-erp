// Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on("Mom From Division", {
 	onload: function(frm) {
        if (!frm.doc.from_user) {
            frm.set_value("from_user", frappe.session.user);
        }
    }
 });
