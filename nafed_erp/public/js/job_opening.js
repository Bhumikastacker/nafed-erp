// ---------------- LIST VIEW FILTER ----------------
frappe.listview_settings['Job Opening'] = {
    onload(listview) {
        frappe.route_options = {
            status: ["in", ["Open"]]
        };
    }
};

// ---------------- FORM SCRIPT ----------------
frappe.ui.form.on("Job Opening", {
    refresh(frm) {
        // ❌ DO NOT set form read-only
        // ❌ DO NOT touch connections
        // ✅ Just refresh fields normally
        frm.refresh_fields();
    },

    // ---------------- DATE VALIDATIONS ----------------
    custom_written_exam_date(frm) {
        validate_past_dates(frm, "custom_written_exam_date");
    },
    custom_gd_exam_date(frm) {
        validate_past_dates(frm, "custom_gd_exam_date");
    },
    posted_on(frm) {
        validate_past_dates(frm, "posted_on");
    },

    // ---------------- FINAL VALIDATE ----------------
    validate(frm) {

        /* ================= Application Fee Category ================= */
        let fee_categories = [];

        (frm.doc.custom_application_fees_category || []).forEach(row => {
            if (fee_categories.includes(row.category)) {
                frappe.msgprint({
                    title: __("Duplicate Category"),
                    message: __("Application Fee Category <b>{0}</b> is already added.", [row.category]),
                    indicator: "red"
                });
                frappe.validated = false;
            }
            fee_categories.push(row.category);
        });

        /* ================= Qualification & Marks ================= */
        let qualifications = [];

        (frm.doc.custom_qualification_and_marks || []).forEach(row => {

            if (qualifications.includes(row.qualification_type)) {
                frappe.msgprint({
                    title: __("Duplicate Qualification"),
                    message: __("Qualification <b>{0}</b> is already added.", [row.qualification_type]),
                    indicator: "red"
                });
                frappe.validated = false;
            }

            if (row.qualification_marks && row.qualification_marks > 100) {
                frappe.msgprint({
                    title: __("Invalid Marks"),
                    message: __("Qualification Marks cannot be more than <b>100%</b>."),
                    indicator: "red"
                });
                frappe.validated = false;
            }

            qualifications.push(row.qualification_type);
        });
    }
});

// ---------------- HELPERS ----------------
function validate_past_dates(frm, fieldname) {
    const today = frappe.datetime.get_today();
    if (frm.doc[fieldname] && frm.doc[fieldname] < today) {
        frappe.msgprint({
            title: __("Message"),
            message: __("You cannot select a past date. Please choose today or a future date."),
            indicator: "red"
        });
        frm.set_value(fieldname, null);
    }
}
