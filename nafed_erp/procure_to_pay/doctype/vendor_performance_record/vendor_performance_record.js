// Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Vendor Performance Record", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on('Vendor Performance Record', {

    refresh: function(frm) {
        frm.trigger('show_ops_badge');

        // Add 'Fetch Module Data' button on Draft
        if (frm.doc.docstatus === 0 && frm.doc.vendor_id) {
            frm.add_custom_button('Fetch Module Data', function() {
                frm.trigger('fetch_auto_scores');
            }, 'Actions');
        }
    },

    // Auto-fetch vendor details when vendor selected
    vendor_id: function(frm) {
        if (!frm.doc.vendor_id) return;
        frappe.db.get_value(
            'Vendor Registration', frm.doc.vendor_id,
            ['vendor_name', 'vendor_code', 'workflow_state'],
            function(v) {
                frm.set_value('vendor_name', v.vendor_name);
                frm.set_value('vendor_code', v.vendor_code);
                if (!['Active','HO Approved'].includes(v.workflow_state)) {
                    frappe.msgprint({
                        message: 'Vendor is not Active: ' + v.workflow_state,
                        indicator: 'red'
                    });
                }
            }
        );
    },

    // Recalculate OPS live as officer enters scores
    kpi_scores_on_form_rendered: function(frm) {
        frm.trigger('calculate_live_ops');
    },

    calculate_live_ops: function(frm) {
        if (!frm.doc.kpi_scores || !frm.doc.kpi_scores.length) return;
        let ops = 0;
        frm.doc.kpi_scores.forEach(row => {
            if (row.score && row.weightage) {
                // FIX: normalize score/5 × weightage
                ops += (row.score / 5) * row.weightage;
            }
        });
        ops = Math.round(ops * 100) / 100;
        frm.set_value('overall_performance_score', ops);

        let rating = 'Poor';
        if (ops >= 90)      rating = 'Excellent';
        else if (ops >= 75) rating = 'Good';
        else if (ops >= 60) rating = 'Satisfactory';
        else if (ops >= 40) rating = 'Needs Improvement';
        frm.set_value('rating_category', rating);
        frm.trigger('show_ops_badge');
},
    show_ops_badge: function(frm) {
        const ops = frm.doc.overall_performance_score || 0;
        const rating = frm.doc.rating_category || '';
        const colors = {
            'Excellent':        'green',
            'Good':             'blue',
            'Satisfactory':     'yellow',
            'Needs Improvement':'orange',
            'Poor':             'red'
        };
        const color = colors[rating] || 'grey';
        if (ops > 0) {
            frm.set_df_property('overall_performance_score', 'description',
                `<span style="color:${color};font-size:14px;font-weight:bold">`,
                `OPS: ${ops} — ${rating}</span>`
            );
        }
    },

    // Fetch auto-scores from ERPNext modules
    fetch_auto_scores: function(frm) {
        if (!frm.doc.vendor_id || !frm.doc.period_start_date
                || !frm.doc.period_end_date) {
            frappe.msgprint('Set Vendor, Start Date and End Date first.');
            return;
        }
        frappe.call({
            method: 'nafed_erp.procure_to_pay.doctype'
                   + '.vendor_performance_record.vendor_performance_record'
                   + '.auto_fetch_module_scores',
            args: {
                vendor_id:  frm.doc.vendor_id,
                start_date: frm.doc.period_start_date,
                end_date:   frm.doc.period_end_date,
            },
            callback: function(r) {
                if (!r.message) return;
                const auto_scores = r.message;
                // Map fetched scores to KPI child table rows
                frm.doc.kpi_scores.forEach(function(row) {
                    if (auto_scores[row.kpi_parameter] !== undefined) {
                        frappe.model.set_value(row.doctype, row.name,
                            'auto_score', auto_scores[row.kpi_parameter]);
                        frappe.model.set_value(row.doctype, row.name,
                            'score', auto_scores[row.kpi_parameter]);
                        frappe.model.set_value(row.doctype, row.name,
                            'data_source', 'Auto-fetched');
                    }
                });
                frm.refresh_field('kpi_scores');
                frm.trigger('calculate_live_ops');
                frappe.show_alert({
                    message: 'Module data fetched for '
                             + Object.keys(auto_scores).length + ' KPIs',
                    indicator: 'green'
                });
            }
        });
    },
});

// Child table: recalculate weighted_score when score changes
frappe.ui.form.on('KPI Score', {
    score: function(frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        if (row.score && row.weightage) {
            const ws = Math.round(row.score * row.weightage) / 100;
            frappe.model.set_value(cdt, cdn, 'weighted_score', ws);
        }
        frm.trigger('calculate_live_ops');
    },
    weightage: function(frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        if (row.score && row.weightage) {
            const ws = Math.round(row.score * row.weightage) / 100;
            frappe.model.set_value(cdt, cdn, 'weighted_score', ws);
        }
        frm.trigger('calculate_live_ops');
    },
});

frappe.ui.form.on("Vendor Performance Record", {
    onload: function(frm) {

            let kpis = [
                "Timeliness of Delivery",
                "Quality Compliance",
                "Quantity Accuracy",
                "Documentation & Invoice Accuracy",
                "Response to Queries",
                "Contract Adherence",
                "Financial Discipline"
            ];

            kpis.forEach(function(kpi) {
                 // check if KPI already exists
            let exists = frm.doc.kpi_scores.some(row => row.kpi_parameter === kpi);

            if (!exists) {

                let row = frm.add_child("kpi_scores");
                row.kpi_parameter = kpi;
            }

            });

            frm.refresh_field("kpi_scores");
        }
    
});
frappe.ui.form.on("Vendor Performance Record", {

    validate: function(frm) {

        let kpis = [];

        frm.doc.kpi_scores.forEach(function(row) {

            if (kpis.includes(row.kpi_parameter)) {

                frappe.throw("Duplicate KPI Parameter not allowed: " + row.kpi_parameter);

            }

            kpis.push(row.kpi_parameter);

        });

    }

});