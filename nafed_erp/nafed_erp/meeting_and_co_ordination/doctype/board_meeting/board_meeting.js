frappe.ui.form.on("Board Meeting", {

   
   meeting_type: function(frm) {

        if (!frm.doc.meeting_type) return;

        // Step 1: Get Meeting Type Code
        frappe.db.get_list('Meeting Type', {
            filters: { name: frm.doc.meeting_type },
            fields: ['code']
        }).then(data => {

            if (!data || data.length === 0) return;

            let code = data[0].code;   // ✅ Correct way

            


            if (code === 'agm') {

                frappe.db.get_list('Board Members', {
                    fields: ['name', 'email']
                }).then(records => {

                    frm.clear_table("attendance");

                    records.forEach(d => {
                        let row = frm.add_child("attendance");
                        row.board_member = d.name;
                        row.email = d.email;
                        row.show = 1;
                    });

                    frm.refresh_field("attendance");
                });
            }
            
            else {

                frappe.db.get_list('BOD List', {
                    filters: { meeting_type: frm.doc.meeting_type },
                    fields: ['name1', 'designation', 'email']
                }).then(records => {
					console.log("Meeting Type Code:", code, frm.doc.meeting_type);
                    frm.clear_table("attendance");

                    records.forEach(d => {
                        let row = frm.add_child("attendance");
                        row.name1 = d.name1;
                        row.designation = d.designation;
                        row.email = d.email;
                        row.show = 0;
                    });

                    frm.refresh_field("attendance");
                });
            }

        });
    },
    // ✅ Refresh event
    refresh: function(frm) {

        console.log("dddddddddddddddddd", frm.doc.docstatus, frm.doc.workflow_state);

        // ✅ MOM Button
        if (frm.doc.docstatus === 0 && !frm.doc.linked_mom && frm.doc.workflow_state === "Attendance Recorded") {

            frm.add_custom_button("MOM Draft", function () {

                frappe.model.with_doctype("Meeting MoM", () => {

                    let nafed_meeting = frappe.model.get_new_doc("Meeting MoM");
                    nafed_meeting.meeting = frm.doc.name;

                    frappe.set_route("Form", "Meeting MoM", nafed_meeting.name);
                });

            });
        }

        // ✅ Agenda Button
        if (!frm.doc.__islocal) {
            if (frm.doc.docstatus === 0 && !frm.doc.linked_agenda && frm.doc.workflow_state === "Draft") {

                frm.add_custom_button("Submit Agenda", function () {

                    frappe.model.with_doctype("Meeting Agenda", () => {

                        let nafed_meeting = frappe.model.get_new_doc("Meeting Agenda");
                        nafed_meeting.meeting = frm.doc.name;

                        frappe.set_route("Form", "Meeting Agenda", nafed_meeting.name);
                    });

                });
            }
        }
    }
});
