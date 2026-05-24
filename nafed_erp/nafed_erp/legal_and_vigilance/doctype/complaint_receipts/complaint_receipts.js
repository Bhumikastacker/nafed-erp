frappe.ui.form.on("Complaint Receipts", {
    refresh(frm) {

        frm.add_custom_button("Add Remarks", function () {

            // ❌ Restriction when Closed
            if (frm.doc.workflow_state === "Closed") {
                frappe.msgprint({
                    title: __("Not Allowed"),
                    message: __("Complaint is Closed. Please reopen it using Action button to add remarks."),
                    indicator: "red"
                });
                return;
            }

            // ✅ Normal flow
            frappe.prompt(
                [
                    {
                        fieldname: "remark_text",
                        fieldtype: "Text Editor",
                        label: "Add Remarks",
                        reqd: 0
                    }
                ],
                function(values) {

                    let text = $("<div>").html(values.remark_text).text().trim();

                    if (!text) {
                        frappe.msgprint({
                            title: __("Validation Error"),
                            message: __("Please add some remarks. Spaces or empty remarks are not allowed."),
                            indicator: "red"
                        });
                        return;
                    }

                    let row = frm.add_child("logs");

                    row.action_taken_by = frappe.session.user;
                    row.action_taken_on = frappe.datetime.get_today();
                    row.remarks = values.remark_text;

                    frm.refresh_field("logs");
                    frm.save();

                },
                __("Remarks"),
                __("Submit")
            );
        });
    }
});