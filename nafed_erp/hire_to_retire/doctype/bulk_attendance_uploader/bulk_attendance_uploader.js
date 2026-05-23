frappe.ui.form.on("Bulk Attendance Uploader", {
    refresh(frm) {
        frm.add_custom_button("Generate Attendance", () => {
            frappe.prompt([
                {
                    label: "Status",
                    fieldname: "status",
                    fieldtype: "Select",
                    options: "Present\nAbsent\nWork From Home\nOn Duty\nHalf Day",
                    reqd: 1
                }
            ],
            (values) => {
                frappe.call({
                    method: "nafed_erp.hire_to_retire.doctype.bulk_attendance_uploader.bulk_attendance_uploader.generate_attendance_for_checkins",
                    args: {
                        docname: frm.doc.name,
                        status: values.status
                    },
                    callback: () => frappe.msgprint("Attendance Generated Successfully")
                });
            });
        });
    }
});
