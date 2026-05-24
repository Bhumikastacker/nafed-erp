
frappe.ui.form.on('Jute Work Order', {

    // =========================
    // ONLOAD
    // =========================
    onload_post_render: function(frm) {
        setTimeout(() => {
            calculate_total_preview(frm);
            toggle_gunny_add_row(frm);

        }, 300);
    },

    // =========================
    // REFRESH
    // =========================
    refresh: async function(frm) {
        toggle_gunny_add_row(frm);


        //  BUTTON (ONLY AFTER SUBMIT)
        if (frm.doc.docstatus == 1) {

            frm.add_custom_button('Create Delivery Tracking', () => {

                frappe.new_doc('Dispatch Details', {
                    work_order_ref_no: frm.doc.name,
                    date_of_issue: frm.doc.date_of_issue,
                    date_of_dispatch: frm.doc.dispatch_by,
                    quantity: frm.doc.total_quantity
                }, (doc) => {

                    // =====================
                    // ITEMS (ONLY add_child)
                    // =====================
                    (frm.doc.gunny_bag_details_table || []).forEach(row => {

                        let child = frappe.model.add_child(doc, 'Dispatch Item Details', 'item_details');

                        Object.assign(child, {
                            gunny_bag_name: row.gunny_bag_name,
                            gunny_bag_length_in_cm: row.gunny_bag_length_in_cm,
                            gunny_bag_width_in_cm: row.gunny_bag_width_in_cm,
                            gunny_bag_weight: row.gunny_bag_weight,
                            gunny_bag_uom: row.gunny_bag_uom,
                            gunny_bag_capacity: row.gunny_bag_capacity,
                            gunny_bag_capacity_uom: row.gunny_bag_capacity_uom,
                            unit_price: row.unit_price,
                            quantity_required: row.quantity_required
                        });

                    });

                    // =====================
                    // DELIVERY (ONLY add_child)
                    // =====================
                    (frm.doc.delivery_location_table || []).forEach(row => {

                        let child = frappe.model.add_child(doc, 'Delivery Location Details', 'delivery_details');

                        Object.assign(child, {
                            location_name: row.location_name,
                            location_address: row.location_address,
                            location_contact: row.location_contact,
                            gunny_bags_req: row.gunny_bags_req
                        });

                    });

                });

            }, 'Create');
        }

        // =========================
        // DEFAULT VALUES
        // =========================
        if (frm.is_new()) {

            if (!frm.doc.date_of_issue) {
                frm.set_value('date_of_issue', frappe.datetime.get_today());
            }

            if (!frm.doc.dispatch_by) {
                frm.set_value('dispatch_by', frappe.datetime.get_today());
            }
        }

        // =========================
        // DUPLICATE CASE FIX
        // =========================
        if (frm.is_new() && frm.doc.amended_from) {
            frm.set_value('indent_reference_no', null);
        }

        // =========================
        // SUBMITTED DOC LOGIC
        // =========================
        if (frm.doc.docstatus === 1) {

            frm.dashboard.clear_headline();

            // DISPATCH CHECK
            let dispatch_res = await frappe.db.get_list('Dispatch Details', {
                filters: {
                    work_order_ref_no: frm.doc.name
                },
                fields: ['name'],
                limit: 1
            });

            if (dispatch_res.length > 0) {
                let d = dispatch_res[0].name;
                frm.dashboard.add_indicator(`Dispatch: ${d}`, 'orange');
            } else {
                frm.dashboard.add_indicator('No Dispatch', 'gray');
            }

            // INVOICE STATUS
            if (frm.doc.ref) {

                let r = await frappe.db.get_value('Sales Invoice', frm.doc.ref,
                    ['name', 'status', 'docstatus']
                );

                let si = r.message;

                if (si) {

                    let color = "blue";

                    if (si.status === "Paid") color = "green";
                    else if (si.status === "Unpaid") color = "red";
                    else if (si.status === "Overdue") color = "orange";
                    else if (si.docstatus === 0) color = "gray";

                    frm.dashboard.add_indicator(`Invoice: ${si.name} (${si.status})`, color);

                } else {
                    frm.dashboard.add_indicator('Invoice Not Found', 'red');
                }

            } else {
                frm.dashboard.add_indicator('No Invoice', 'gray');
            }
        }

        // =========================
        // PREVIEW CALCULATION
        // =========================
        if (frm.doc.docstatus === 0) {
            setTimeout(() => {
                calculate_total_preview(frm);
                toggle_gunny_add_row(frm);

            }, 200);
        }
    },

    // =========================
    // VALIDATE
    // =========================
    validate: async function(frm) {

        if (!frm.doc.indent_reference_no) return;

        let res = await frappe.db.get_list('Jute Work Order', {
            filters: {
                indent_reference_no: frm.doc.indent_reference_no,
                docstatus: 1,
                name: ["!=", frm.doc.name]
            },
            fields: ['name'],
            limit: 1
        });

        if (res.length > 0) {

            let jwo = res[0].name;

            frappe.throw(`
                Jute Work Order already exists:
                <a href="/app/jute-work-order/${jwo}" target="_blank">${jwo}</a>
            `);
        }
    },

    // =========================
    // FETCH FROM INDENT
    // =========================
    indent_reference_no: function(frm) {

        if (!frm.doc.indent_reference_no) return;

        frm.clear_table('gunny_bag_details_table');
        frm.clear_table('delivery_location_table');

        frappe.model.with_doc('Indent', frm.doc.indent_reference_no, function() {

            let indent = frappe.model.get_doc('Indent', frm.doc.indent_reference_no);

            // ITEMS
            (indent.bag_table || []).forEach(row => {
                let child = frm.add_child('gunny_bag_details_table');

                Object.assign(child, {
                    gunny_bag_name: row.gunny_bag_name,
                    gunny_bag_weight:row.gunny_bag_weight,
                    gunny_bag_uom:row.gunny_bag_uom,
                    gunny_bag_capacity:row.gunny_bag_capacity,
                    gunny_bag_capacity_uom:row.gunny_bag_capacity_uom,
                    unit_price: row.rate || row.unit_price,
                    quantity_required: row.quantity_required
                });
            });

            // DELIVERY
            (indent.location_table || []).forEach(row => {
                let child = frm.add_child('delivery_location_table');

                Object.assign(child, {
                    location_name: row.location_name,
                    location_address:row.location_address,
                    location_contact:row.location_contact,
                    gunny_bags_req: row.gunny_bags_req
                });
            });

            frm.refresh_fields();

            setTimeout(() => {
                calculate_total_preview(frm);
            }, 200);
        });
    }
});


// =========================
// CHILD EVENTS
// =========================
frappe.ui.form.on('Delivery Location Details', {
    gunny_bags_req: function(frm) {
        calculate_total_preview(frm);
    },
    delivery_location_table_add: function(frm) {
        calculate_total_preview(frm);
    },
    delivery_location_table_remove: function(frm) {
        calculate_total_preview(frm);
    }
});

frappe.ui.form.on('Gunny Items Child', {
    unit_price: function(frm) {
        calculate_total_preview(frm);
    },
    gunny_bag_details_table_add: function(frm) {
        toggle_gunny_add_row(frm);
    },

    gunny_bag_details_table_remove: function(frm) {
        toggle_gunny_add_row(frm);
    }

});


// =========================
// CALCULATION
// =========================
function calculate_total_preview(frm) {

    let total_qty = 0;

    (frm.doc.delivery_location_table || []).forEach(row => {
        total_qty += flt(row.gunny_bags_req);
    });

    let rate = 0;

    if (frm.doc.gunny_bag_details_table?.length) {
        rate = flt(frm.doc.gunny_bag_details_table[0].unit_price || 0);
    }

    let total_price = total_qty * rate;

    frm.set_value("total_quantity", total_qty);
    frm.set_value("total_price", total_price);
}
// =========================
// GUNNY ROW CONTROL (ONLY 1 ROW)
// =========================
function toggle_gunny_add_row(frm) {

    let row_count = frm.doc.gunny_bag_details_table?.length || 0;

    let grid = frm.fields_dict.gunny_bag_details_table.grid;

    if (row_count >= 1) {
        grid.cannot_add_rows = true;
        grid.wrapper.find('.grid-add-row, .grid-insert-row, .grid-insert-row-below').hide();
    } else {
        grid.cannot_add_rows = false;
        grid.wrapper.find('.grid-add-row, .grid-insert-row, .grid-insert-row-below').show();
    }

    frm.refresh_field("gunny_bag_details_table");
}