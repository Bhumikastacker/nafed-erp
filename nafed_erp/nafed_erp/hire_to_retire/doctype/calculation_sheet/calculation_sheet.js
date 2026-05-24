// Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on('Calculation Sheet', {
    // Math triggers
    compensation_days: function(frm) { calculate_all_math(frm); },
    from_date: function(frm) { calculate_all_math(frm); },
    to_date: function(frm) { calculate_all_math(frm); },

    refresh: function(frm) {
        frm.remove_custom_button(__('Get Employees'), __('Actions'));
        frm.remove_custom_button(__('Create Additional Salary'), __('Actions'));

        // 1. Get Employees Button
        if (frm.doc.docstatus === 0 && frm.doc.type) {
            frm.add_custom_button(__('Get Employees'), function() {
                let method = (frm.doc.type === 'Ex-Gratia') ? 'get_ex_gratia_data' : 'calculate_dynamic_arrears';
                let target_table = (frm.doc.type === 'Ex-Gratia') ? 'ex_gratia_result_table' : 'component_details';

                frm.call({
                    doc: frm.doc,
                    method: method,
                    callback: function(r) {
                        if (r.message) {
                            frm.clear_table(target_table);
                            r.message.forEach(d => {
                                let row = frm.add_child(target_table);
                                if (frm.doc.type === 'Arrears' || frm.doc.type === 'Recoveries') {
                                    // ARREAR & RECOVERY Mapping
                                    row.employee = d.employee;
                                    row.component = d.component;
                                    row.previous_amount = d.previous_amount || 0;
                                    row.revised_amount = d.revised_amount || 0;
                                } else {
                                    // EX-GRATIA Mapping (Using your specific logic)
                                    row.employee = d.employee; row.basic = d.basic || 0;
                                    row.da = d.da || 0; row.hra = d.hra || 0;
                                    row.total = d.total || 0;
                                }
                            });
                            frm.refresh_field(target_table);
                            calculate_all_math(frm); 
                        }
                    }
                });
            }, __("Actions"));
        }

        // 2. Create Additional Salary Button
        if (frm.doc.docstatus === 1) {
            frm.add_custom_button(__('Create Additional Salary'), function() {
                frappe.confirm(__('Do you want to create Additional Salary?'), () => {
                    frm.call({ doc: frm.doc, method: 'create_additional_salaries', callback: () => { frm.reload_doc(); } });
                });
            }, __("Actions"));
        }

        // =========================================================================
        // The filter logic has been added from here (at the end of the refresh function).
        // =========================================================================
        frm.set_query("salary_component", function() {
            if (frm.doc.type === "Recoveries") {
                return {
                    filters: { "type": "Deduction" } // Show only deduction salary components.
                };
            } else {
                return {
                    filters: [
                        ["Salary Component", "type", "!=", "Deduction"] // Show all salary components except deductions.
                    ]
                };
            }
        });
    
    },

    // Arrear/Recovery % fetch
    salary_component: function(frm) {
        if (frm.doc.salary_component && (frm.doc.type === 'Arrears' || frm.doc.type === 'Recoveries')) {
            frappe.call({
                method: "frappe.client.get_value",
                args: { doctype: "Salary Component", filters: { name: frm.doc.salary_component }, fieldname: "custom_default_percentage_" },
                callback: function(r) {
                    if (r.message) frm.set_value('current_compensation_', r.message.custom_default_percentage_ || 0);
                }
            });
        }
    }
});

// --- CALCULATION LOGIC ---
function calculate_all_math(frm) {
    if (!frm.doc.from_date || !frm.doc.to_date) return;

    let period_days = moment(frm.doc.to_date).diff(moment(frm.doc.from_date), 'days') + 1;
    let months = (period_days / 30).toFixed(2);
    frm.set_value('number_of_months', months);

    let g_total = 0;
    let type = frm.doc.type;

    if (type === 'Ex-Gratia') {
        let comp_days = flt(frm.doc.compensation_days) || 30;
        (frm.doc.ex_gratia_result_table || []).forEach(row => {
            let result = (flt(row.total) / 30) * comp_days;
            // Naye field names mapping
            row.ex_gratia_final_amount = result;
            row.ex_gratia_manual_amount = result; 
            g_total += flt(row.ex_gratia_manual_amount);
        });
        frm.refresh_field('ex_gratia_result_table');
    } 
    else if (type === 'Arrears') {
        (frm.doc.component_details || []).forEach(row => {
            let diff = flt(row.revised_amount) - flt(row.previous_amount);
            row.final_amount = diff * flt(frm.doc.number_of_months);
            g_total += flt(row.final_amount);
        });
        frm.refresh_field('component_details');
    }
    else if (type === 'Recoveries') {
        (frm.doc.component_details || []).forEach(row => {
            let diff = flt(row.previous_amount) - flt(row.revised_amount);
            row.final_amount = diff * flt(frm.doc.number_of_months);
            g_total += flt(row.final_amount);
        });
        frm.refresh_field('component_details');
    }
    frm.set_value('grand_total', g_total);
}

// Manual Override Triggers for Grand Total
frappe.ui.form.on('Ex Gratia Summary', {
    ex_gratia_manual_amount: function(frm) {
        let total = 0;
        frm.doc.ex_gratia_result_table.forEach(row => { total += flt(row.ex_gratia_manual_amount); });
        frm.set_value('grand_total', total);
    }
});

frappe.ui.form.on('Component Sheet', {
    final_amount: function(frm) {
        let total = 0;
        frm.doc.component_details.forEach(row => { total += flt(row.final_amount); });
        frm.set_value('grand_total', total);
    }
});


// =====================================The code below is running perfectly.=====================================================================

// frappe.ui.form.on('Calculation Sheet', {
//     // Math triggers
//     compensation_days: function(frm) { calculate_all_math(frm); },
//     from_date: function(frm) { calculate_all_math(frm); },
//     to_date: function(frm) { calculate_all_math(frm); },

//     refresh: function(frm) {
//         frm.remove_custom_button(__('Get Employees'), __('Actions'));
//         frm.remove_custom_button(__('Create Additional Salary'), __('Actions'));

//         // 1. Get Employees Button
//         if (frm.doc.docstatus === 0 && frm.doc.type) {
//             frm.add_custom_button(__('Get Employees'), function() {
//                 let method = (frm.doc.type === 'Ex-Gratia') ? 'get_ex_gratia_data' : 'calculate_dynamic_arrears';
//                 let target_table = (frm.doc.type === 'Ex-Gratia') ? 'ex_gratia_result_table' : 'component_details';

//                 frm.call({
//                     doc: frm.doc,
//                     method: method,
//                     callback: function(r) {
//                         if (r.message) {
//                             frm.clear_table(target_table);
//                             r.message.forEach(d => {
//                                 let row = frm.add_child(target_table);
//                                 if (frm.doc.type === 'Arrears' || frm.doc.type === 'Recoveries') {
//                                     // ARREAR & RECOVERY Mapping
//                                     row.employee = d.employee;
//                                     row.component = d.component;
//                                     row.previous_amount = d.previous_amount || 0;
//                                     row.revised_amount = d.revised_amount || 0;
//                                 } else {
//                                     // EX-GRATIA Mapping (Using your specific logic)
//                                     row.employee = d.employee; row.basic = d.basic || 0;
//                                     row.da = d.da || 0; row.hra = d.hra || 0;
//                                     row.total = d.total || 0;
//                                 }
//                             });
//                             frm.refresh_field(target_table);
//                             calculate_all_math(frm); 
//                         }
//                     }
//                 });
//             }, __("Actions"));
//         }

//         // 2. Create Additional Salary Button
//         if (frm.doc.docstatus === 1) {
//             frm.add_custom_button(__('Create Additional Salary'), function() {
//                 frappe.confirm(__('Do you want to create Additional Salary?'), () => {
//                     frm.call({ doc: frm.doc, method: 'create_additional_salaries', callback: () => { frm.reload_doc(); } });
//                 });
//             }, __("Actions"));
//         }
//     },

//     // Arrear/Recovery % fetch
//     salary_component: function(frm) {
//         if (frm.doc.salary_component && (frm.doc.type === 'Arrears' || frm.doc.type === 'Recoveries')) {
//             frappe.call({
//                 method: "frappe.client.get_value",
//                 args: { doctype: "Salary Component", filters: { name: frm.doc.salary_component }, fieldname: "custom_default_percentage_" },
//                 callback: function(r) {
//                     if (r.message) frm.set_value('current_compensation_', r.message.custom_default_percentage_ || 0);
//                 }
//             });
//         }
//     }
// });

// // --- CALCULATION LOGIC ---
// function calculate_all_math(frm) {
//     if (!frm.doc.from_date || !frm.doc.to_date) return;

//     let period_days = moment(frm.doc.to_date).diff(moment(frm.doc.from_date), 'days') + 1;
//     let months = (period_days / 30).toFixed(2);
//     frm.set_value('number_of_months', months);

//     let g_total = 0;
//     let type = frm.doc.type;

//     if (type === 'Ex-Gratia') {
//         let comp_days = flt(frm.doc.compensation_days) || 30;
//         (frm.doc.ex_gratia_result_table || []).forEach(row => {
//             let result = (flt(row.total) / 30) * comp_days;
//             // Naye field names mapping
//             row.ex_gratia_final_amount = result;
//             row.ex_gratia_manual_amount = result; 
//             g_total += flt(row.ex_gratia_manual_amount);
//         });
//         frm.refresh_field('ex_gratia_result_table');
//     } 
//     else if (type === 'Arrears') {
//         (frm.doc.component_details || []).forEach(row => {
//             let diff = flt(row.revised_amount) - flt(row.previous_amount);
//             row.final_amount = diff * flt(frm.doc.number_of_months);
//             g_total += flt(row.final_amount);
//         });
//         frm.refresh_field('component_details');
//     }
//     else if (type === 'Recoveries') {
//         (frm.doc.component_details || []).forEach(row => {
//             let diff = flt(row.previous_amount) - flt(row.revised_amount);
//             row.final_amount = diff * flt(frm.doc.number_of_months);
//             g_total += flt(row.final_amount);
//         });
//         frm.refresh_field('component_details');
//     }
//     frm.set_value('grand_total', g_total);
// }

// // Manual Override Triggers for Grand Total
// frappe.ui.form.on('Ex Gratia Summary', {
//     ex_gratia_manual_amount: function(frm) {
//         let total = 0;
//         frm.doc.ex_gratia_result_table.forEach(row => { total += flt(row.ex_gratia_manual_amount); });
//         frm.set_value('grand_total', total);
//     }
// });

// frappe.ui.form.on('Component Sheet', {
//     final_amount: function(frm) {
//         let total = 0;
//         frm.doc.component_details.forEach(row => { total += flt(row.final_amount); });
//         frm.set_value('grand_total', total);
//     }
// });

