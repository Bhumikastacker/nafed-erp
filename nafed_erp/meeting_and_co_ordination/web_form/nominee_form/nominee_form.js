frappe.ready(function() {

    frappe.web_form.on('membership_id', (field, value) => {

        if (value) {

            frappe.call({
                method: "frappe.client.get_value",
                args: {
                    doctype: "Nominee  Form",
                    filters: {
                        membership_id: value
                    },
                    fieldname: "name"
                },
                callback: function(r) {

                    if (r.message && r.message.name) {
                        frappe.msgprint("Nominee Form is already submitted for this Membership ID.");
                        frappe.web_form.set_value("membership_id", "");
                        return;
                    }

                    frappe.call({
                        method: "frappe.client.get",
                        args: {
                            doctype: "Board Members",
                            name: value
                        },
                        callback: function(res) {
                            if (res.message) {
                                let doc = res.message;

                                frappe.web_form.set_value("agm_year", doc.agm_year);
                                frappe.web_form.set_value("state", doc.state);
                                frappe.web_form.set_value("district", doc.district);
                                frappe.web_form.set_value("society_name", doc.society_name_1);
                                frappe.web_form.set_value("share_capital", doc.share_capital);
                            }
                        }
                    });
                }
            });
        }
    });

});


frappe.ready(function () {

    frappe.web_form.set_value(
        'application_date',
        frappe.datetime.get_today()
    );

});