// Copyright (c) 2025, CSM Technologies Pvt Ltd and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Record Fixed Deposit Details", {
// 	refresh(frm) {

// 	},
// });
// Copyright (c) 2025, CSM Technologies Pvt Ltd and contributors
// For license information, please see license.txt
frappe.ui.form.on("Track Deposit Dates and Tenure", {
    deposit_date(frm, cdt, cdn) {
        calculate_child_maturity(frm, cdt, cdn);
    },
    tenure(frm, cdt, cdn) {
        calculate_child_maturity(frm, cdt, cdn);
    }
});

function calculate_child_maturity(frm, cdt, cdn) {
    const row = frappe.get_doc(cdt, cdn);

    if (row.deposit_date && row.tenure) {
        // calculate maturity for this row
        let maturity = frappe.datetime.add_months(row.deposit_date, row.tenure);

        // set in child row
        frappe.model.set_value(cdt, cdn, "maturity_date", maturity);

        // refresh child table
        frm.refresh_field("track_deposit_dates_and_tenure");

        // also update parent maturity_date
        frm.set_value("maturity_date", maturity);
    }
}
