// Copyright (c) 2025, CSM Technologies Pvt Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on("Assign Lessee to Property", {
	refresh: function(frm) {
        if (!frm.doc.__islocal) {
             frm.add_custom_button(
                    __("Renewal/Extension"),
                    () =>
                        frappe.set_route("List", "Lease Renewal_Extension", {
                            'lease_assignment_id': frm.doc.name
                        }),
                    __("Take Action")
                );
            }
        }
});
