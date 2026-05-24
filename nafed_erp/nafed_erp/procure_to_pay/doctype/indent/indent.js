// =====================================
// INDENT → BUTTON + SLA FILTER + JWO CHECK
// =====================================
frappe.ui.form.on('Indent', {

    refresh: function(frm) {
                // 🔹 Bag table restriction
        toggle_bag_table_add_row(frm);

        set_sla_filter(frm);
        calculate_indent_totals(frm);

        if (frm.doc.docstatus === 1) {

            frappe.db.get_list('Jute Work Order', {
                filters: {
                    indent_reference_no: frm.doc.name
                },
                fields: ['name', 'docstatus'],
                limit: 1
            }).then(res => {

                frm.dashboard.clear_headline();

                let jwo_exists = res.length > 0;
                let is_submitted = jwo_exists && res[0].docstatus === 1;

                // =============================
                // SHOW JWO STATUS
                // =============================
                if (jwo_exists) {

                    let jwo_name = res[0].name;

                    frm.dashboard.set_headline(`
                        <span style="color:green;font-weight:bold;">
                            Jute Work Order already created:
                            <a href="/app/jute-work-order/${jwo_name}" target="_blank">
                                ${jwo_name}
                            </a>
                        </span>
                    `);

                    frm.dashboard.add_indicator(
                        is_submitted ? 'JWO Submitted' : 'JWO Draft',
                        is_submitted ? 'blue' : 'orange'
                    );
                }

                // =============================
                // BUTTON ONLY IF NOT SUBMITTED
                // =============================
                if (!is_submitted) {

                    frm.add_custom_button(__('Create Jute Work Order'), function () {

                        frappe.call({
                            method: 'nafed_erp.procure_to_pay.doctype.indent.indent.create_jute_work_order',
                            args: {
                                indent_name: frm.doc.name
                            },
                            callback: function(r) {

                                if (r.message) {
                                    frappe.msgprint(__('Jute Work Order Created: ') + r.message);
                                    frappe.set_route('Form', 'Jute Work Order', r.message);
                                }

                            }
                        });

                    }, __('Actions'));
                }

            });
        }
    },

    state: function(frm) {
        frm.set_value('sla', null);
        set_sla_filter(frm);
    }
});



// =====================================
// LOCATION TABLE EVENTS (INDENT)
// =====================================
frappe.ui.form.on('Delivery Location Details', {

    gunny_bags_req: function(frm) {
        if (frm.doc.doctype === "Indent") {
            calculate_indent_totals(frm);
        }
    },

    location_table_add: function(frm) {
        calculate_indent_totals(frm);
    },

    location_table_remove: function(frm) {
        calculate_indent_totals(frm);
    }
});


// =====================================
// BAG TABLE EVENTS (INDENT)
// =====================================
frappe.ui.form.on('Gunny Items Child', {

    // 🔹 When row is added
    bag_table_add: function(frm, cdt, cdn) {
        toggle_bag_table_add_row(frm);
        calculate_indent_totals(frm);
    },

    // 🔹 When row is removed
    bag_table_remove: function(frm, cdt, cdn) {
        toggle_bag_table_add_row(frm);
        calculate_indent_totals(frm);
    },

    // 🔹 When unit price changes
    unit_price: function(frm, cdt, cdn) {
        calculate_indent_totals(frm);
    },

    // 🔹 Fetch data from Item Master
    gunny_bag_name: function(frm, cdt, cdn) {

        let row = locals[cdt][cdn];

        if (!row.gunny_bag_name) return;

        frappe.db.get_doc('Jute Bag Item Master', row.gunny_bag_name)
            .then(item => {

                // Set values
                row.gunny_bag_weight = item.wt;
                row.gunny_bag_uom = item.wt_uom;
                row.gunny_bag_capacity = item.capacity;
                row.gunny_bag_capacity_uom = item.capacity_uom;
                row.unit_price = item.rate;

                frm.refresh_field('bag_table');

                // Recalculate totals
                calculate_indent_totals(frm);
            });
    }
});
// =====================================
// BAG TABLE RESTRICTION FUNCTION
// =====================================
function toggle_bag_table_add_row(frm) {

    let row_count = frm.doc.bag_table ? frm.doc.bag_table.length : 0;

    if (row_count >= 1) {

        frm.get_field("bag_table").grid.cannot_add_rows = true;

        let grid = frm.fields_dict.bag_table.grid.wrapper;
        grid.find('.grid-add-row').hide();
        grid.find('.grid-insert-row').hide();
        grid.find('.grid-insert-row-below').hide();

    } else {

        frm.get_field("bag_table").grid.cannot_add_rows = false;

        let grid = frm.fields_dict.bag_table.grid.wrapper;
        grid.find('.grid-add-row').show();
        grid.find('.grid-insert-row').show();
        grid.find('.grid-insert-row-below').show();
    }

    frm.refresh_field("bag_table");
}


// =====================================
// INDENT TOTAL CALCULATION
// =====================================
function calculate_indent_totals(frm) {

    let total_qty = 0;
    let rate = 0;

    // TOTAL QTY from location table
    (frm.doc.location_table || []).forEach(row => {
        total_qty += flt(row.gunny_bags_req);
    });

    // RATE from bag table (first row)
    if (frm.doc.bag_table && frm.doc.bag_table.length > 0) {
        rate = flt(frm.doc.bag_table[0].rate || frm.doc.bag_table[0].unit_price);
    }

    // SET VALUES
    frm.set_value('total_quantity', total_qty);
    frm.set_value('total_price', total_qty * rate);

    frm.refresh_field('total_quantity');
    frm.refresh_field('total_price');
}


// =====================================
// SLA FILTER
// =====================================
function set_sla_filter(frm) {
    frm.set_query('sla', function() {
        return {
            filters: frm.doc.state ? { state: frm.doc.state } : {}
        };
    });
}