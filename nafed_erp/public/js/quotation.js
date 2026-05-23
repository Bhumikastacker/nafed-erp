frappe.ui.form.on('Quotation', {

    refresh(frm) {

        if (!frm.is_new() && frm.doc.quotation_to === "Customer") {

            frm.add_custom_button('Send Email to Customer', function () {

                if (!frm.doc.party_name) {
                    frappe.msgprint("Customer not selected");
                    return;
                }

                // Fetch email directly from Customer doctype
                frappe.db.get_value('Customer', frm.doc.party_name, 'email_id')
                    .then(r => {

                        let email = r.message.email_id;

                        if (!email) {
                            frappe.msgprint({
                                title: "No Email Found",
                                message: "Customer does not have an email address.",
                                indicator: "red"
                            });
                            return;
                        }

                        // Dummy success message
                        frappe.msgprint({
                            title: "Email Sent",
                            message: `Quotation sent to ${email}`,
                            indicator: "green"
                        });

                    });

            }, "Actions");

        }
    }

});