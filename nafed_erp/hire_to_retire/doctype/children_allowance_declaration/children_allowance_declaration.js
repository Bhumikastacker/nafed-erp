

frappe.ui.form.on('Children Allowance Declaration', {

    onload: function(frm) {

        if (frm.is_new()) {
            const logged_user = frappe.session.user;

            frappe.db.get_value("Employee", { user_id: logged_user }, "name")
                .then(r => {
                    if (r.message && r.message.name) {
                        let emp = r.message.name;

                        frm.set_value("employee", emp).then(() => {
                            frm.trigger("employee"); 
                        });

                    } else {
                        frappe.msgprint("No Employee record linked with this user.");
                    }
                });

            // 🔹 Fetch Allowance Amount from HR Settings
            frappe.db.get_single_value("HR Settings", "children_allowance_amount")
                .then(amount => {
                    if (amount) frm.set_value("amount", amount);
                });
        }
    },

    employee: function(frm) {

        if (!frm.doc.employee) return;

        frappe.db.get_doc("Employee", frm.doc.employee).then(employee => {

            // -------------------------------
            // 1. SET BASIC EMPLOYEE FIELDS
            // -------------------------------
            frm.set_value({
                employee_name: employee.employee_name || '',
                designation: employee.designation || '',
                department: employee.department || '',
                company: employee.company || '',
                section: employee.custom_section || ''
            });

            // -------------------------------
            // 2. FETCH CUSTOM_DETAILS CHILD TABLE
            // -------------------------------
            if (employee.custom_details && employee.custom_details.length > 0) {

                frm.clear_table("children_details");

                employee.custom_details.forEach(row => {
                    let child = frm.add_child("children_details");

                    child.child_name = row.child_name || '';
                    child.date_of_birth = row.date_of_birth || '';
                    child.school_name = row.school_name || '';
                    child.class_studying_in = row.class_studying_in || '';
                    child.not_applicable = row.not_applicable || '';
                });

                frm.refresh_field("children_details");
            }
        });
    }
});


// -------------------------------
// VALIDATION FOR AGE LIMIT
// -------------------------------
frappe.ui.form.on('Children Allowance Declaration', {
    validate: async function(frm) {

        let children = frm.doc.children_details || [];
        if (children.length === 0) return;

        // Get Min & Max from HR Settings
        let min_age = await frappe.db.get_single_value("HR Settings", "children_allowance_min_age_limit");
        let max_age = await frappe.db.get_single_value("HR Settings", "children_allowance_max_age_limit");

        min_age = parseInt(min_age || 0);
        max_age = parseInt(max_age || 0);

        let today = new Date();

        for (let row of children) {

            if (!row.date_of_birth) continue;

            let dob = new Date(row.date_of_birth);

            // Age Calculation
            let age = today.getFullYear() - dob.getFullYear();
            let diff = today.getMonth() - dob.getMonth();
            if (diff < 0 || (diff === 0 && today.getDate() < dob.getDate())) {
                age--;
            }

            // Validate Age
            if (age < min_age || age > max_age) {
                frappe.msgprint({
                    title: "Not Eligible",
                    indicator: "red",
                    message: `Age must be between ${min_age} and ${max_age} years for the Children Allowance Declaration.`
                });

                frappe.validated = false;
                return false;
            }
        }
    }
});
// CHILD TABLE EVENTS
frappe.ui.form.on('Children Details', {

    child_name: function(frm) {
        calculate_children_allowance(frm);
    },

    not_applicable: function(frm) {
        calculate_children_allowance(frm);
    },

    children_details_remove: function(frm) {
        calculate_children_allowance(frm);
    }
});


// CALCULATION FUNCTION
function calculate_children_allowance(frm) {

    let count = 0;

    (frm.doc.children_details || []).forEach(row => {
        if (!row.not_applicable) {
            count++;
        }
    });

    frappe.db.get_single_value("HR Settings", "children_allowance_amount")
        .then(amount => {

            amount = parseFloat(amount || 0);

            let total = amount * count;

            frm.set_value("amount", total);
        });
}

