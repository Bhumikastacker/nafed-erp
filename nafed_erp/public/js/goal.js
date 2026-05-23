frappe.ui.form.on("Goal", {

    // Trigger when End Date is changed
    end_date: function(frm) {
        if (frm.doc.start_date && frm.doc.end_date) {

            // Validate: End Date should not be earlier than Start Date
            if (frm.doc.end_date < frm.doc.start_date) {
                frappe.msgprint(__("End Date cannot be earlier than Start Date"));

                // 2. Clear the invalid End Date value
                frm.set_value('end_date', '');
            }
        }
    },

    // Trigger when Start Date is changed
    start_date: function(frm) {
        if (frm.doc.start_date && frm.doc.end_date) {

            // Validate: Start Date should not be later than End Date
            if (frm.doc.end_date < frm.doc.start_date) {
                frappe.msgprint(__("Start Date cannot be later than End Date"));

                // Clear the invalid Start Date value
                frm.set_value("start_date", '');
            }
        }
    }

});