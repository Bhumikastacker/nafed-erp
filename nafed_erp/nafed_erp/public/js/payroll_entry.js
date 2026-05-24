frappe.ui.form.on("Payroll Entry", {
    validate: async function (frm) {

        if (!frm.doc.custom_employment_type || !frm.doc.start_date) {
            return;
        }

        // Fetch allowed days from Employment Type
        const r = await frappe.db.get_value(
            "Employment Type",
            frm.doc.custom_employment_type,
            "custom_payroll_entry_date"
        );

        if (!r.message || !r.message.custom_payroll_entry_date) {
            return;
        }

        let allowed_days = cint(r.message.custom_payroll_entry_date);

        // Payroll Entry start date
        let payroll_start_date = frm.doc.start_date;

        // Today's date
        let today = frappe.datetime.get_today();

        // Difference in days
        let diff_days = frappe.datetime.get_diff(today, payroll_start_date);

        // ❌ Start date is in the future
        if (diff_days < 0) {
            frappe.msgprint({
                title: __("Invalid Date"),
                message: __("Payroll Entry start date cannot be a future date."),
                indicator: "red"
            });
            frappe.validated = false;
            return;
        }

        // ❌ Difference is less than allowed days
        if (diff_days < allowed_days) {
            frappe.msgprint({
                title: __("Not Allowed"),
                message: __(
                    "Payroll Entry is allowed only after <b>{0} days</b> for the selected Employment Type.",
                    [allowed_days, diff_days]
                ),
                indicator: "orange"
            });
            frappe.validated = false;
        }

        // ✅ Allowed → save will continue
    },
    validate: function (frm) {
        // Stop if start_date is not entered
        if (!frm.doc.start_date) return;

        const start_date = frm.doc.start_date;
        const today = frappe.datetime.get_today(); // format: yyyy-mm-dd

        // If start_date is in the future
        if (start_date > today) {
            frappe.msgprint({
                title: __("Invalid Start Date"),
                message: __("Start Date cannot be a future date or future month."),
                indicator: "red"
            });

            // Prevent form submission
            frappe.validated = false;
        }
    }
});

