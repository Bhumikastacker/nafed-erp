frappe.ui.form.on('CSM Db', {
    generate_attendance: function(frm) {
        frappe.call({
            method: "nafed_erp.hire_to_retire.doctype.csm_db.csm_db.generate_attendance_for_checkins",
            args: {
                docname: frm.doc.name
            },
            freeze: true,
            freeze_message: "Generating Attendance...",
            callback: function(r) {
                if (!r.exc) {
                    frappe.msgprint("Attendance generated successfully!");
                    frm.reload_doc();
                }
            }
        });
    }
});
