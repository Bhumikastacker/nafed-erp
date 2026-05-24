// Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on("Increment Log", {
    employee(frm) {
        set_new_basic_options(frm);
    },

    onload(frm){
        set_new_basic_options(frm);
        frm.set_query("employee", () => {
            return {
                filters: {
                    company: frm.doc.company,
                    status : "Active"
                }
            };
        });
    },
    company(frm) {
        // reset employee when company changes
        frm.set_value("employee", null);

        frm.set_query("employee", () => {
            return {
                filters: {
                    company: frm.doc.company,
                    status : "Active"
                }
            };
        });
    },
    refresh(frm){
        set_new_basic_options(frm);
    },
    after_save(frm) {
        frm.reload_doc();   // 🔥 reloads clean state from DB
    },

    new_basic(frm) {

        let new_basic = flt(frm.doc.new_basic);
        let old_basic = flt(frm.doc.old_basic);

        if (!new_basic) {
            frm.set_value("increment_amount", 0);
            return;
        }

        // ❌ Validation
        if (new_basic <= old_basic) {
            frappe.msgprint("New Basic must be greater than Old Basic");

            frm.set_value("new_basic", old_basic);
            frm.set_value("increment_amount", 0);
            return;
        }

        // ✅ Calculate increment
        let increment = new_basic - old_basic;

        frm.set_value("increment_amount", increment);
    }
});

// ----------------------------
// 🔥 MAIN FUNCTION
// ----------------------------
function set_new_basic_options(frm) {

    if (!frm.doc.employee) {
        frm.set_df_property("new_basic", "options", []);
        return;
    }

    // ✅ Step 1: Get Employee
    frappe.call({
        method: "frappe.client.get",
        args: {
            doctype: "Employee",
            name: frm.doc.employee
        },
        callback: function(emp_res) {

            let grade = emp_res.message?.grade;

            if (!grade) {
                frm.set_df_property("new_basic", "options", []);
                return;
            }

            // ✅ Step 2: Get Grade
            frappe.call({
                method: "frappe.client.get",
                args: {
                    doctype: "Employee Grade",
                    name: grade
                },
                callback: function(grade_res) {

                    let options = [];

                    let current_basic = flt(frm.doc.old_basic);

                    (grade_res.message.custom_basic_pays || []).forEach(row => {

                        let basic = flt(row.basic_pay);

                        // 🔥 only allow higher slabs
                        if (basic > current_basic) {
                            options.push(basic);
                        }
                    });

                    // ✅ Sort (important for UX)
                    options.sort((a, b) => a - b);

                    // ✅ Set options
                    frm.set_df_property(
                        "new_basic",
                        "options",
                        options.join("\n")
                    );
                }
            });
        }
    });
}