frappe.ui.form.on('Employee Grade', {
    employee_grade(frm) {
        if (frm.doc.employee_grade) {
            frappe.call({
                method: "frappe.client.get",
                args: {
                    doctype: "Employee Grade",
                    name: frm.doc.employee_grade
                },
                callback(r) {
                    if (r.message) {
                        // Clear existing child table
                        frm.clear_table("basic_pays");

                        // Loop through child table rows
                        (r.message.basic_pays || []).forEach(row => {
                            let child = frm.add_child("basic_pays");
                            child.component = row.component;
                            child.amount = row.amount;
                        });

                        frm.refresh_field("basic_pays");
                    }
                }
            });
        } else {
            frm.clear_table("basic_pays");
            frm.refresh_field("basic_pays");
        }
    }
});



frappe.ui.form.on("Employee Grade", {
    refresh(frm) {
        set_grade_pay_filter(frm);
    },
    onload(frm) {
        set_grade_pay_filter(frm);
    },
    custom_pay_band(frm) {
        set_grade_pay_filter(frm);
    }
});

function set_grade_pay_filter(frm) {
    frm.set_query("custom_grade_pay", function() {
        return {
            filters: {
                pay_band: frm.doc.custom_pay_band || ""   // filter by selected pay band
            }
        };
    });
}