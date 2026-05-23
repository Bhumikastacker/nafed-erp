frappe.ui.form.on("Salary Structure", {
    refresh(frm) {
        override_deduction_filter(frm);
    },
    company(frm){
        override_deduction_filter(frm);
    }
});

function override_deduction_filter(frm) {
    if (!frm.doc.company) return;

    frm.fields_dict["deductions"].grid
        .get_field("salary_component").get_query = function () {
            return {
                filters: {
                    component_type: "deduction",
                    company: frm.doc.company,
                    custom_is_additional_deduction_component: 0
                },
                query: "nafed_erp.pf_trust.doc_events.salary_component.get_salary_component_custom"
            };
        };
}