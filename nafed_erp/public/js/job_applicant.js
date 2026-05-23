frappe.ui.form.on("Job Applicant", {
    refresh(frm) {
        // Wait until connections are rendered
        setTimeout(() => {
            // Find Interview connection button and hide the "+"
            $('a:contains("Interview")')
                .closest('.document-link')
                .find('.btn-new')
                .hide();
        }, 300);
    },
    refresh: function(frm) {
        // Run only after document is saved
        if (!frm.is_new()) {
            if (frm.doc.status === "Accepted" || frm.doc.status === "Rejected") {
                frm.set_df_property("status", "read_only", 1);
            } else {
                frm.set_df_property("status", "read_only", 0);
            }
        }
    },
});

frappe.ui.form.on("Job Applicant", {
 refresh: function (frm) {
        // Disable all connection clicks
        $('.form-dashboard a, .form-dashboard .btn').css({
            'pointer-events': 'none',
            'cursor': 'not-allowed',
            'opacity': '0.6'
        });
    }
});