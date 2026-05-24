frappe.ui.form.on("Learning Path", {
    refresh(frm) {
        if (frm.doc.status === "Approved") {
            frm.set_df_property("core_courses", "read_only", 1);
            frm.set_df_property("elective_courses", "read_only", 1);
        }
        if (frm.doc.workflow_state === "Approved" && frm.doc.docstatus === 1) {

            frm.add_custom_button("Create Training", function () {

                frappe.model.with_doctype("Nafed Training Meeting", () => {

                    let nafed_meeting = frappe.model.get_new_doc("Nafed Training Meeting");

                    // Map parent field
                    nafed_meeting.learning_path = frm.doc.name;

                    // SAFE child table mapping
                    (frm.doc.employee_details || []).forEach(emp => {

                        let row = frappe.model.add_child(
                            nafed_meeting,
                            "Nafed Training Attendee",
                            "attendees"
                        );

                        row.employee = emp.employee;
                        row.employee_name = emp.employee_name;
                        row.company_email = emp.company_email;
                        row.personal_email = emp.personal_email;
                    });

                    frappe.set_route("Form", "Nafed Training Meeting", nafed_meeting.name);
                });

            });
        }
    }
});
