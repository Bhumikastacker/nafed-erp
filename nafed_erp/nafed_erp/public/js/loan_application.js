frappe.ui.form.on('Loan Application', {
    loan_product: function(frm) {
        // Wait for 'Fetch From' values to populate after Loan Product selection
        setTimeout(() => {
            if (frm.doc.custom_loan_type) {
                fetch_housing_sub_categories(frm);
            }
        }, 1500);
    },

    custom_loan_type: function(frm) {
        // Triggered when Loan Type field changes
        if (frm.doc.custom_loan_type) {
            fetch_housing_sub_categories(frm);
        }
    }
});

function fetch_housing_sub_categories(frm) {
    let loan_type = frm.doc.custom_loan_type;

    // Fetch the Loan Type master document to access its child table
    frappe.db.get_doc('Loan Type', loan_type).then(doc => {
        let options = [""]; // Initialize with a blank option

        // Check if the child table 'housing_rules' has data
        if (doc.housing_rules && doc.housing_rules.length > 0) {
            doc.housing_rules.forEach(row => {
                if (row.sub_category) {
                    options.push(row.sub_category);
                }
            });

            // Set the dropdown options as a newline-separated string
            let options_string = options.join("\n");
            frm.set_df_property('custom_housing_sub_category', 'options', options_string);

            // Auto-select the value if there is only one valid option in the list
            if (options.length === 2) {
                frm.set_value('custom_housing_sub_category', options[1]);
            }

            frm.refresh_field('custom_housing_sub_category');
        }
    });
}