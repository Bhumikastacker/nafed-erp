function generate_next_employee_number(frm) {
    // If already present, do nothing
    if (frm.doc.employee_number) return;

    frappe.db.get_list("Employee", {
        fields: ["employee_number"],
        order_by: "CAST(employee_number AS UNSIGNED) DESC",
        limit: 1
    }).then(res => {
        let next_num = 1;

        if (res.length && res[0].employee_number) {
            const last = parseInt(res[0].employee_number);
            if (!isNaN(last)) next_num = last + 1;
        }

        frm.set_value("employee_number", next_num.toString());
    });
    
}

frappe.ui.form.on("Employee", {

    refresh(frm) {
        if (frm.is_new()) {
            generate_next_employee_number(frm);
        }
    },

    before_save(frm) {
        // Double safety: ensure employee_number is never empty
        if (frm.is_new() && !frm.doc.employee_number) {
            generate_next_employee_number(frm);
        }
    },
    custom_same_as_present_address: function(frm){
        if(frm.doc.custom_same_as_present_address == 1){
           frm.set_value("custom_pmtcity", frm.doc.custom_pcity);
           frm.set_value("custom_pmtpin", frm.doc.custom_ppin);
           frm.set_value("custom_permanent_state", frm.doc.custom_present_state);
           frm.set_value("custom_permanent_street", frm.doc.custom_present_street);
           frm.set_value("permanent_address", frm.doc.current_address);
           frm.set_value("permanent_accommodation_type", frm.doc.current_accommodation_type);
           frm.set_value("custom_permanent_telephone_number", frm.doc.custom_telph);
        }
        else{
            frm.set_value("custom_pmtcity", "");
           frm.set_value("custom_pmtpin","");
           frm.set_value("custom_permanent_state", "");
           frm.set_value("custom_permanent_street", "");
           frm.set_value("permanent_address", "");
           frm.set_value("permanent_accommodation_type", "");
           frm.set_value("custom_permanent_telephone_number", "");
        }
    },
    reports_to(frm) {
        console.log("Bhagggggggggggggggggggggg")
        if (!frm.doc.designation) {
            frm.set_value("reports_to", "");
            frappe.throw(__("Designation is required before selecting Reports To"));
        }
    },
    designation: function (frm) {
        if (!frm.doc.designation) {
            frm.set_df_property("reports_to", "reqd", 0);
            return;
        }

        frappe.db.get_value(
            "Designation",
            frm.doc.designation,
            "custom_reports_to",
            function (r) {
                if (r && r.custom_reports_to) {
                    // Make reports_to mandatory
                    frm.set_df_property("reports_to", "reqd", 1);
                } else {
                    // Remove mandatory
                    frm.set_df_property("reports_to", "reqd", 0);
                }
            }
        );
    },
    validate: function(frm) {
        if (frm.doc.pan_number) {
            let pan = frm.doc.pan_number.toUpperCase();

            // Regex for PAN
            let pan_regex = /^[A-Z]{5}[0-9]{4}[A-Z]{1}$/;

            if (!pan_regex.test(pan)) {
                frappe.msgprint({
                    message: __("Invalid PAN Number"),
                });
                frappe.validated = false;
            } else {
                frm.set_value("pan_number", pan);
            }
        }
    }
});



frappe.ui.form.on("Employee", {
    onload(frm) {
        set_basic_pay_options(frm);
    },

    refresh(frm) {
        set_basic_pay_options(frm);
    },

    grade(frm) {
        set_basic_pay_options(frm);
    }
});


function set_basic_pay_options(frm) {
    // If no grade selected, clear options
    if (!frm.doc.grade) {
        frm.set_df_property("custom_basic_pay", "options", []);
        return;
    }

    frappe.call({
        method: "frappe.client.get",
        args: {
            doctype: "Employee Grade",
            name: frm.doc.grade
        },
        callback: function(r) {
            if (!r.message) return;

            let options = [];

            // Loop through child table (custom_basic_pays)
            (r.message.custom_basic_pays || []).forEach(row => {
                options.push(row.basic_pay);   // Change if needed
            });

            // Add options to select field
            frm.set_df_property("custom_basic_pay", "options", options.join("\n"));
        }
    });
}

frappe.ui.form.on('Employee', {
    refresh(frm) {

        const is_admin = frappe.session.user === "Administrator";
        const is_checker = frappe.user_roles.includes("Z Employee - Checker");
        const is_workspace = frappe.user_roles.includes("Workspace Manager");

        console.log("Admin:", is_admin);
        console.log("Checker:", is_checker);
        console.log("Workspace Manager:", is_workspace);

        // 🔥 If Admin → ALWAYS SHOW field
        if (is_admin) {
            frm.set_df_property('employment_type', 'hidden', 0);
            console.log("Admin detected → Showing employment_type");
            return;
        }

        // 🔥 If BOTH roles → HIDE
        if (is_checker && is_workspace) {
            frm.set_df_property('employment_type', 'hidden', 1);
            console.log("Hiding field because both roles found");
        }

        // 🔥 Otherwise → SHOW
        else {
            frm.set_df_property('employment_type', 'hidden', 0);
            console.log("Showing field because roles not matching");
        }
    }
});

// addded by mayuri 
frappe.ui.form.on('Employee', {
    refresh(frm) {
        enforce_two_children_limit(frm);
    }
});

function enforce_two_children_limit(frm) {
    const fieldname = 'custom_details';   
    const max_rows = 2;

    const grid = frm.get_field(fieldname)?.grid;
    if (!grid) return;

    const original_refresh = grid.refresh;
    grid.refresh = function () {
        original_refresh.call(this);

        let rows = frm.doc[fieldname] || [];

        if (rows.length > max_rows) {
            rows.splice(max_rows);   // keep only first 2`
            frm.refresh_field(fieldname);

            frappe.msgprint({
                title: __('Limit Reached'),
                message: __('Only 2 children are allowed'),
                indicator: 'red'
            });
        }

        // 🔒 Disable / Enable Add Row button
        const add_btn = grid.wrapper.find('.grid-add-row');
        if (rows.length >= max_rows) {
            add_btn.prop('disabled', true).addClass('disabled');
        } else {
            add_btn.prop('disabled', false).removeClass('disabled');
        }
    };
}