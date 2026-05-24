// =====================================
// SAFE FLOAT
// =====================================
const flt = (val) => parseFloat(val) || 0;


// =====================================
// DISABLE ADD ROW
// =====================================
function disable_child_table_add(frm) {

    const tables = ["procurement", "movement_lifting_qtymt", "table_jxbr"];

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
// SYNC TABLES
// =====================================
function sync_all_tables(frm) {

    frm.clear_table("movement_lifting_qtymt");
    frm.clear_table("table_jxbr");

    (frm.doc.procurement || []).forEach(row => {

        if (row.district) {

            frm.add_child("movement_lifting_qtymt", {
                district: row.district,
                centre: row.centre
            });

            frm.add_child("table_jxbr", {
                district: row.district,
                centre: row.centre
            });
        }
    });

    frm.refresh_field("movement_lifting_qtymt");
    frm.refresh_field("table_jxbr");
}


// =====================================
// MAIN FORM
// =====================================
frappe.ui.form.on('Update Wheat Procurement Progress', {

   refresh(frm) {

    if (frm.doc.procurement_target_id) {
        disable_child_table_add(frm);
    }

},



    procurement_target_id(frm) {
        if (!frm.doc.procurement_target_id) return;

        frm.clear_table("procurement");
        frm.clear_table("movement_lifting_qtymt");
        frm.clear_table("table_jxbr");

        frappe.db.get_doc("Procurement Target", frm.doc.procurement_target_id)
            .then(doc => {

                (doc.commodity_details || []).forEach(row => {
                    frm.add_child("procurement", {
                        district: row.district,
                        centre: row.centre
                    });
                });

                frm.refresh_field("procurement");

                setTimeout(() => {
                    sync_all_tables(frm);
                    disable_child_table_add(frm);
                }, 100);
            });
    }
});


// =====================================
// PROCUREMENT CHILD
// =====================================
frappe.ui.form.on('Wheat Procurement  Child', {

    faq(frm, cdt, cdn) {

        let row = locals[cdt][cdn];

        frappe.model.set_value(cdt, cdn, "total",
            flt(row.faq) + flt(row.urs)
        );
    },

    urs(frm, cdt, cdn) {

        let row = locals[cdt][cdn];

        frappe.model.set_value(cdt, cdn, "total",
            flt(row.faq) + flt(row.urs)
        );
    }
});


frappe.ui.form.on('Wheat Delivery Child', {

    total_issued(frm) {
        // agar future me use karna ho
    },

    total_lifted_to_mills(frm, cdt, cdn) {
        calculate_delivery_total(cdt, cdn);
    },

    total_faq_quantity_sent_to_mills(frm, cdt, cdn) {
        calculate_delivery_total(cdt, cdn);
    },

    total_urs_quantity_sent_to_mills(frm) {
        // isko manual edit nahi karna ideally
    }
});


// COMMON FUNCTION
function calculate_delivery_total(cdt, cdn) {

    let row = locals[cdt][cdn];

    let lifted = flt(row.total_lifted_to_mills);
    let faq = flt(row.total_faq_quantity_sent_to_mills);

    frappe.model.set_value(
        cdt,
        cdn,
        "total_urs_quantity_sent_to_mills",
        lifted + faq
    );
}
// =====================================
// DEPOT CHILD
// =====================================
frappe.ui.form.on('Wheat Delivery Depot Child', {

    faq_qty_accepted_by_depot(frm, cdt, cdn) {
        calculate_depot_total(cdt, cdn);
    },

    urs_qty_accepted_by_depot(frm, cdt, cdn) {
        calculate_depot_total(cdt, cdn);
    }
});


// COMMON FUNCTION
function calculate_depot_total(cdt, cdn) {

    let row = locals[cdt][cdn];

    let faq = flt(row.faq_qty_accepted_by_depot);
    let urs = flt(row.urs_qty_accepted_by_depot);

    frappe.model.set_value(
        cdt,
        cdn,
        "total_accepted_by_depot",
        faq + urs
    );
}