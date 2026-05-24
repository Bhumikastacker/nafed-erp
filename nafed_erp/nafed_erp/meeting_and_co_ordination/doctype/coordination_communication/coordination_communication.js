// Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on("Coordination Communication", {


    onload: function(frm) {
	console.log(frappe.route_options.send_to)
        if (frappe.route_options) {
            frm.set_value("send_to", frappe.route_options.send_to);
        }

    }

});
