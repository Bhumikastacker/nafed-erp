
// =====================================
// SAFE FLOAT
// =====================================
const flt = (val) => parseFloat(val) || 0;


// =====================================
// DISABLE ADD ROW
// =====================================
function disable_child_table_add(frm) {

    const tables = ["procurement", "table_xgxr", "others"];

    tables.forEach(fieldname => {

        let grid = frm.get_field(fieldname)?.grid;

        if (grid) {
            grid.cannot_add_rows = true;
            $(grid.wrapper).find('.grid-add-row').hide();
            $(grid.wrapper).find('.grid-add-multiple-rows').hide();
        }
    });
}


// =====================================
// CLEAN TOTAL ROW (AVOID DUPLICATE)
// =====================================
function clean_total(frm, fieldname) {

    let table = frm.doc[fieldname] || [];
    let found = false;

    frm.doc[fieldname] = table.filter(row => {
        if (!row.is_total_row) return true;

        if (!found) {
            found = true;
            return true;
        }
        return false;
    });

    frm.refresh_field(fieldname);
}


// =====================================
// PROCUREMENT TOTAL
// =====================================
function get_or_create_total_row(frm) {

    let table = frm.doc.procurement || [];
    let total = table.find(r => r.is_total_row);

    if (!total) {
        total = frm.add_child('procurement');
        total.is_total_row = 1;
        total.centre = "Total";

    }

    return total;
}

function update_procurement_total(frm) {

    let table = frm.doc.procurement || [];
    if (!table.length) return;

    clean_total(frm, "procurement");

    let t = { o:0, ov:0, p:0, pv:0, c:0, cv:0 };

    table.forEach(row => {
        if (row.is_total_row) return;

        t.o += flt(row.opening_qty);
        t.ov += flt(row.value__rs_in_lacs);
        t.p += flt(row.procurement);
        t.pv += flt(row.procurement_value);
        t.c += flt(row.closing);
        t.cv += flt(row.closing_value);
    });

    let total = get_or_create_total_row(frm);

    total.opening_qty = t.o;
    total.value__rs_in_lacs = t.ov;
    total.procurement = t.p;
    total.procurement_value = t.pv;
    total.closing = t.c;
    total.closing_value = t.cv;

    frm.refresh_field('procurement');
}


// =====================================
// CMR TOTAL
// =====================================
function update_cmr_total(frm) {

    let table = frm.doc.table_xgxr || [];
    if (!table.length) return;

    clean_total(frm, "table_xgxr");

    let t = { to_be: 0, delivered: 0, balance: 0 };

    table.forEach(row => {
        if (row.is_total_row) return;

        t.to_be += flt(row.cmr_to_be_delivered);
        t.delivered += flt(row.cmr_delivered);
        t.balance += flt(row.balance_cmr);
    });

    let total = table.find(r => r.is_total_row);

    if (!total) {
        total = frm.add_child('table_xgxr');
        total.is_total_row = 1;
        total.centre = "Total";

    }

    total.cmr_to_be_delivered = t.to_be;
    total.cmr_delivered = t.delivered;
    total.balance_cmr = t.balance;

    frm.refresh_field('table_xgxr');
}


// =====================================
// OTHERS TOTAL
// =====================================
function update_others_total(frm) {

    let table = frm.doc.others || [];
    if (!table.length) return;

    clean_total(frm, "others");

    let total_commission = 0;
    let total_farmers = 0;

    table.forEach(row => {

        if (row.is_total_row) return;

        total_commission += flt(row.commission);
        total_farmers += flt(row.no_of_farmers_benefited);
    });

    let total = table.find(r => r.is_total_row);

    if (!total) {

        total = frm.add_child('others');

        total.is_total_row = 1;
        total.centre = "Total";
    }

    // ✅ TOTALS
    total.commission = total_commission;
    total.no_of_farmers_benefited = total_farmers;frappe.model.set_value(
    total.doctype,
    total.name,
    "no_of_farmers_benefited",
    total_farmers
);

    frm.refresh_field('others');
}
// =====================================
// OTHERS CHILD EVENTS
// =====================================
frappe.ui.form.on('Farmers Benfited Child', {
    no_of_farmers_benefited: function(frm, cdt, cdn) {

        let row = locals[cdt][cdn];

        if (row.is_total_row) return;

        update_others_total(frm);
    },

    form_render: function(frm) {
        update_others_total(frm);
    },

    others_remove: function(frm) {
        update_others_total(frm);
    }
});



// =====================================
// MAIN FORM
// =====================================
frappe.ui.form.on('Update Procurement Progress', {

    refresh(frm) {

        if (frm.doc.procurement_target_id) {
            disable_child_table_add(frm);
        }

        frm.add_custom_button(__('Last Transaction'), () => {

            if (!frm.doc.procurement_target_id) {
                frappe.msgprint("Please select Procurement Target first");
                return;
            }

            frappe.call({
                method: "frappe.client.get_list",
                args: {
                    doctype: "Update Procurement Progress",
                    filters: {
                        procurement_target_id: frm.doc.procurement_target_id,
                        docstatus: 1,
                        name: ["!=", frm.doc.name]
                    },
                    fields: ["name"],
                    order_by: "creation desc",
                    limit: 1
                },
                callback: function(res) {

                    if (res.message && res.message.length) {

                        let last_doc_name = res.message[0].name;

                        frappe.call({
                            method: "frappe.client.get",
                            args: {
                                doctype: "Update Procurement Progress",
                                name: last_doc_name
                            },
                            callback: function(r) {

                                let last_doc = r.message;

                                frm.set_value(
                                    "cmr_to_be_deliverin_percent",
                                    last_doc.cmr_to_be_deliverin_percent || 0
                                );

                                // =====================================
                                // PROCUREMENT TABLE
                                // =====================================
                                (last_doc.procurement || []).forEach(last_row => {

                                    let current_row = (frm.doc.procurement || []).find(row =>
                                        !row.is_total_row &&
                                        row.district === last_row.district &&
                                        row.centre === last_row.centre
                                    );

                                    if (current_row) {

                                        frappe.model.set_value(
                                            current_row.doctype,
                                            current_row.name,
                                            "opening_qty",
                                            flt(last_row.closing)
                                        );
                                    }
                                });

                                frm.refresh_field("procurement");

                                // =====================================
                                // OTHERS TABLE
                                // =====================================
                                (last_doc.others || []).forEach(last_row => {

                                    let current_row = (frm.doc.others || []).find(row =>
                                        !row.is_total_row &&
                                        row.district === last_row.district &&
                                        row.centre === last_row.centre
                                    );

                                    if (current_row) {

                                        frappe.model.set_value(
                                            current_row.doctype,
                                            current_row.name,
                                            "no_of_farmers_benefited",
                                            flt(last_row.no_of_farmers_benefited)
                                        );
                                    }
                                });

                                frm.refresh_field("others");

                                calculate_cmr_table(frm);
                                calculate_commission(frm);
                                update_procurement_total(frm);
                                update_others_total(frm);

                                frappe.msgprint("Last transaction data loaded");
                            }
                        });

                    } else {
                        frappe.msgprint("No previous record found");
                    }
                }
            });

        }, __("Get Items From"));
    },

    // =====================================
    // PROCUREMENT TARGET
    // =====================================
    procurement_target_id(frm) {

        if (!frm.doc.procurement_target_id) return;

        frm.clear_table('procurement');

        frappe.db.get_doc('Procurement Target', frm.doc.procurement_target_id)
            .then(doc => {

                (doc.commodity_details || []).forEach(row => {

                    frm.add_child('procurement', {
                        district: row.district,
                        centre: row.centre,
                        target_quantity: flt(row.target_quantity) 
                    });

                });

                frm.refresh_field('procurement');

                sync_cmr_table(frm);
                sync_farmers_table(frm);

                disable_child_table_add(frm);

                update_procurement_total(frm);
            });
    },

    // =====================================
    // MSP CHANGE
    // =====================================
    msp_per_mt(frm) {

        (frm.doc.procurement || []).forEach(row => {

            if (!row.is_total_row) {
                calculate_all(frm, row.doctype, row.name);
            }
        });

        update_procurement_total(frm);
    },


    // =====================================
    // CMR %
    // =====================================
    cmr_to_be_deliverin_percent(frm) {
        calculate_cmr_table(frm);
    },

// =====================================
// VALIDATION
// =====================================
validate(frm) {

    (frm.doc.procurement || []).forEach(row => {

        let target_qty = flt(row.target_quantity);

        // =====================================
        // ONLY FOR TOTAL ROW
        // =====================================
        if (row.centre === "Total") {

            target_qty = flt(frm.doc.total_allocated_qty_mt);
        }

        // =====================================
        // CLOSING VALIDATION
        // =====================================
        if (flt(row.closing) > target_qty) {

            frappe.throw(
                `Row ${row.idx}: Closing Qty cannot be greater than Target Quantity (${target_qty}) for Centre ${row.centre}`
            );
        }

        // =====================================
        // BALANCE CMR VALIDATION
        // =====================================
        if (flt(row.balance_cmr) < 0) {

            frappe.throw(
                `Row ${row.idx}: Balance CMR cannot be negative for District ${row.district}`
            
                );
            }
        });
    }
});


// =====================================
// CHILD EVENTS
// =====================================
frappe.ui.form.on('Update Procurement Progress Child', {

    opening_qty(frm, cdt, cdn) {
        let r = locals[cdt][cdn];
        if (r.is_total_row) return;

    let procurement = flt(r.procurement);
    let target_qty = flt(r.target_quantity);

    if (procurement > target_qty) {

        frappe.msgprint(
            __("Progressive Procurement cannot be greater than Target Quantity")
        );

        frappe.model.set_value(cdt, cdn, "procurement", target_qty);

        return;
    }

        calculate_all(frm, cdt, cdn);
        update_procurement_total(frm);
    },

    procurement(frm, cdt, cdn) {
        let r = locals[cdt][cdn];
        if (r.is_total_row) return;

        calculate_all(frm, cdt, cdn);
        update_procurement_total(frm);
    },

    procurement_remove(frm) {
        update_procurement_total(frm);
    }
});


// =====================================
// CALCULATION
// =====================================

function calculate_all(frm, cdt, cdn) {

    let row = locals[cdt][cdn];
    if (row.is_total_row) return;

    let opening = flt(row.opening_qty);
    let procurement = flt(row.procurement);
    let target_qty = flt(row.target_quantity);
    let msp = flt(frm.doc.msp_per_mt);

    let closing = opening + procurement;

    // =====================================
    // LIVE VALIDATION
    // =====================================
    if (closing > target_qty) {

        frappe.msgprint({
            title: __('Validation Error'),
            indicator: 'red',
            message: __(
                `Closing Qty cannot be greater than Target Quantity (${target_qty}) for District ${row.district}`
            )
        });

        // Reset procurement
        procurement = Math.max(0, target_qty - opening);

        closing = opening + procurement;

        frappe.model.set_value(cdt, cdn, "procurement", procurement);
    }

    frappe.model.set_value(cdt, cdn, "closing", closing);
    frappe.model.set_value(cdt, cdn, "value__rs_in_lacs", opening * msp);
    frappe.model.set_value(cdt, cdn, "procurement_value", procurement * msp);
    frappe.model.set_value(cdt, cdn, "closing_value", closing * msp);

    calculate_cmr_table(frm);
    calculate_commission(frm);
}


// =====================================
// SYNC TABLES
// =====================================
function sync_cmr_table(frm) {

    frm.clear_table("table_xgxr");

    (frm.doc.procurement || []).forEach(row => {
        if (!row.is_total_row) {
            frm.add_child("table_xgxr", {
                district: row.district,
                centre: row.centre
            });
        }
    });

    frm.refresh_field("table_xgxr");

    calculate_cmr_table(frm);
}

function sync_farmers_table(frm) {

    frm.clear_table("others");

    (frm.doc.procurement || []).forEach(row => {
        if (!row.is_total_row) {
            frm.add_child("others", {
                district: row.district,
                centre: row.centre
            });
        }
    });

    frm.refresh_field("others");

    calculate_commission(frm);
}


// =====================================
// CMR CALCULATION
// =====================================
function calculate_cmr_table(frm) {

    let percent = flt(frm.doc.cmr_to_be_deliverin_percent);

    (frm.doc.table_xgxr || []).forEach(cmr_row => {

        let proc_row = (frm.doc.procurement || []).find(p =>
            !p.is_total_row &&
            p.district === cmr_row.district &&
            p.centre === cmr_row.centre
        );

        if (proc_row) {

            let closing = flt(proc_row.closing);
            let to_be = closing * (percent / 100);

            frappe.model.set_value(cmr_row.doctype, cmr_row.name, "cmr_to_be_delivered", to_be);

            let delivered = flt(cmr_row.cmr_delivered);
            frappe.model.set_value(cmr_row.doctype, cmr_row.name, "balance_cmr", to_be - delivered);
        }
    });

    update_cmr_total(frm);
}


// =====================================
// COMMISSION CALCULATION
// =====================================
function calculate_commission(frm) {

    (frm.doc.others || []).forEach(f_row => {

        let proc_row = (frm.doc.procurement || []).find(p =>
            !p.is_total_row &&
            p.district === f_row.district &&
            p.centre === f_row.centre
        );

        if (proc_row) {

            let closing_value = flt(proc_row.closing_value);
            let commission = closing_value * 0.01;

            frappe.model.set_value(f_row.doctype, f_row.name, "commission", commission);
        }
    });

    update_others_total(frm);
}




// =====================================
// CMR DETAILS VALIDATION
// =====================================

frappe.ui.form.on('CMR Details Child', {

    cmr_delivered(frm, cdt, cdn) {

        let row = locals[cdt][cdn];

        // Skip total row
        if (row.is_total_row) return;

        let delivered = flt(row.cmr_delivered);
        let to_be_delivered = flt(row.cmr_to_be_delivered);

        // =====================================
        // VALIDATION
        // =====================================
        if (delivered > to_be_delivered) {

            frappe.msgprint({
                title: __('Validation Error'),
                indicator: 'red',
                message: __('Balance CMR cannot be negative')
            });

            // Reset delivered value
            delivered = to_be_delivered;

            frappe.model.set_value(
                cdt,
                cdn,
                'cmr_delivered',
                delivered
            );
        }

        // =====================================
        // BALANCE CALCULATION
        // =====================================
        let balance = to_be_delivered - delivered;

        // Extra safety
        if (balance < 0) {
            balance = 0;
        }

        frappe.model.set_value(
            cdt,
            cdn,
            "balance_cmr",
            balance
        );

        update_cmr_total(frm);
    }
});