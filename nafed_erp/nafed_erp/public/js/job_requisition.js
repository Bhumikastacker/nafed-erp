frappe.ui.form.on('Job Requisition', {
    refresh(frm) {
        setTimeout(() => {
            const jobOpeningConn = $("[data-doctype='Job Opening']");
            jobOpeningConn.hide();   // default hide

            if (frm.doc.status && frm.doc.status === "Open & Approved") {
                jobOpeningConn.show();   // show only when status = Open & Approved
            }
        }, 200);
    }
});

frappe.ui.form.on('Job Requisition', {
    validate(frm) {
        if (frm.doc.posting_date && frm.doc.expected_by) {
            if (frm.doc.expected_by < frm.doc.posting_date) {
                frappe.msgprint(__('Expected By Date cannot be earlier than Posting Date'));
                frappe.validated = false;
            }
        }
    }
});

frappe.ui.form.on("Job Requisition", {
    onload(frm) {
        if (!frm.doc.requested_by) {
            frappe.call({
                method: "frappe.client.get_value",
                args: {
                    doctype: "Employee",
                    filters: {
                        user_id: frappe.session.user
                    },
                    fieldname: "name"
                },
                callback: function (r) {
                    if (r.message) {
                        frm.set_value("requested_by", r.message.name);
                    }
                }
            });
        }
    }
});