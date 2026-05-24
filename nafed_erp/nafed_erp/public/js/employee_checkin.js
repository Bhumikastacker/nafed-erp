frappe.ui.form.on("Employee Checkin", {
    refresh(frm) {
        frm._ignore_leave_check = false;
    },
    validate(frm) {
        if (frm._ignore_leave_check) return;

        if (!frm.doc.employee || !frm.doc.time) return;

        frappe.call({
            method: "frappe.client.get_list",
            args: {
                doctype: "Leave Application",
                filters: {
                    employee: frm.doc.employee,
                    status: "Approved"
                },
                fields: ["name", "from_date", "to_date", "leave_type"]
            },
            callback(r) {
                if (r.message && r.message.length > 0) {
                    let checkin_date = frappe.datetime.str_to_obj(frm.doc.time);

                    let leave = r.message.find(l => {
                        let from_date = frappe.datetime.str_to_obj(l.from_date);
                        let to_date = frappe.datetime.str_to_obj(l.to_date);
                        return checkin_date >= from_date && checkin_date <= to_date;
                    });

                    if (leave) {
                        frappe.validated = false;

                        frappe.confirm(
                            `You are on approved leave (${leave.leave_type}) from ${leave.from_date} to ${leave.to_date}. Your attendance will be marked on leave.<br><br>Do you still want to check in?`,
                            () => {
                                frm._ignore_leave_check = true;
                                frm.save();
                            },
                            () => {
                                frappe.msgprint("Check-in cancelled because employee is on approved leave.");
                            }
                        );
                    }
                }
            }
        });
    }
});
