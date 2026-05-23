frappe.web_form.after_save = function () {
    let app_no = frappe.web_form.doc.name;

    frappe.msgprint({
        title: __("Application Submitted Successfully"),
        message: __(
            "Thank you for your registration.<br><br>" +
            "<b>Your Application Number:</b> " + app_no
        ),
        indicator: "green"
    });
};

