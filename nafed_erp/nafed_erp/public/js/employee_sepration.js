
frappe.ui.form.on('Employee Separation', {
    refresh: function(frm) {

        if (!frm.is_new()) {
            let readonly_fields = [
                "employee",
                "employee_name",
                "designation",
                "employee_grade",
                "custom_employee_sepstation_type",
                "company",
                "boarding_begins_on"
            ];

            readonly_fields.forEach(field => {
                frm.set_df_property(field, "read_only", 1);
            });
        }
        const employee_roles = [
            "Employee",
            "Z Employee - View",
            "Z Employee - Manager",
            "Z Employee - Checker",
            "Z Employee - Maker"
        ];

        const hr_roles = [
            "Z HR - Manager",
            "HR - Checker",
            "Z HR - Maker",
            "Z HR Report",
            "HR User",
            "HR Manager"
        ];

        let user_roles = frappe.user_roles || [];

        let has_hr_role = user_roles.some(r => hr_roles.includes(r));
        let has_employee_role = user_roles.some(r => employee_roles.includes(r));

        if (has_hr_role) {
            frm.set_df_property(
                'custom_employee_sepstation_type',
                'options',
                ['Resignation', 'Superannuation', 'Termination', 'CRS', 'VRS', 'Death', 'Dismissal']

            );
        }
        else if (has_employee_role) {
            frm.set_df_property(
                'custom_employee_sepstation_type',
                'options',
                ['Resignation']
            );

            if (frm.doc.custom_employee_sepstation_type !== 'Resignation') {
                frm.set_value('custom_employee_sepstation_type', '');
            }
        }
    }
});

frappe.ui.form.on('Employee Separation', {
        refresh: function (frm) {
        const user_roles = frappe.user_roles || [];

        const hr_roles = [
            'HR User',
            'HR Manager',
            'Z HR - View',
            'Z HR - Manager',
            'Z HR - Maker',
            'HR - Checker',
            'Z HR Report'
        ];

        const is_hr_user = user_roles.some(role => hr_roles.includes(role));

        if (!is_hr_user) {
          
            frm.set_df_property('notify_users_by_email', 'hidden', 1);

            frm.set_df_property('exit_summary', 'hidden', 1);
        } else {
         
            frm.set_df_property('notify_users_by_email', 'hidden', 0);
            frm.set_df_property('exit_summary', 'hidden', 0);
        }
    }
});




