// Copyright (c) 2025, CSM Technologies Pvt Ltd and contributors
// For license information, please see license.txt


frappe.ui.form.on("LTC Period", {
    period_start: function(frm) {
        set_year_slab(frm);
    },
    period_end: function(frm) {
        set_year_slab(frm);
    }
});

function set_year_slab(frm) {
    if (frm.doc.period_start && frm.doc.period_end) {
        let start_year = frappe.datetime.str_to_obj(frm.doc.period_start).getFullYear();
        let end_year = frappe.datetime.str_to_obj(frm.doc.period_end).getFullYear();
        frm.set_value("year_slab", `${start_year}-${end_year}`);
    }
}
