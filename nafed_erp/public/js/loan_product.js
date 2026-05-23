frappe.ui.form.on("Loan Product",{
    refresh(frm){
        frm.set_query("custom_salary_component", function() {
        return {
            "filters": {
                "custom_is_loan_component": 1,
            }
        };
    });
    }
})