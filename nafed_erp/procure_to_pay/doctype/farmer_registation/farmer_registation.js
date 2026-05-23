// Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
// For license information, please see license.txt


frappe.ui.form.on("Farmer Registation", {
    source(frm) {
        if (frm.doc.source === "Nafed(Manual)") {
            frm.set_value("registration_date", frappe.datetime.get_today());
        }
    }

});
