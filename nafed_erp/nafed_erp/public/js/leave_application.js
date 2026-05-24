frappe.ui.form.on("Leave Application", {
    refresh(frm) {
        if (!frm.is_new() && frm.doc.docstatus === 0) {
            frm.add_custom_button("Send Approval Email", () => {
                frappe.call({
                    method: "nafed_erp.hire_to_retire.doc_events.leave_application.send_leave_approval_mail",
                    args: {
                        docname: frm.doc.name
                    },
                    callback: function(r) {
                        if (!r.exc) {
                            frappe.msgprint({
                                title: __("Success"),
                                message: r.message || __("Notification sent successfully."),
                                indicator: "green"
                            });
                        }
                    }
                });
            });
        }
    },
// by mayuri 
// Hide the 5th column (Leaves Pending Approval)  
    make_dashboard: function (frm) {
        let leave_details;
        let lwps;

        if (frm.doc.employee) {
            frappe.call({
                method: "hrms.hr.doctype.leave_application.leave_application.get_leave_details",
                async: false,
                args: {
                    employee: frm.doc.employee,
                    date: frm.doc.from_date || frm.doc.posting_date,
                },
                callback: function (r) {
                    if (!r.exc && r.message["leave_allocation"]) {
                        leave_details = r.message["leave_allocation"];
                    }
                    lwps = r.message["lwps"];
                },
            });

            $("div").remove(".form-dashboard-section.custom");

            frm.dashboard.add_section(
                frappe.render_template("leave_application_dashboard", {
                    data: leave_details,
                }),
                __("Allocated Leaves"),
            );
            frm.dashboard.show();

            // Hide the 5th column (Leaves Pending Approval)
            setTimeout(() => {
                let $section = $(".form-dashboard-section:contains('Allocated Leaves')");
                $section.find("th:nth-child(5), td:nth-child(5)").hide();
            }, 100);

            let allowed_leave_types = Object.keys(leave_details).concat(lwps);
            frm.set_query("leave_type", function () {
                return {
                    filters: [["leave_type_name", "in", allowed_leave_types]],
                };
            });
        }
    }

});


