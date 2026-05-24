
// =====================================
// MAIN FORM
// =====================================
frappe.ui.form.on('Procurement Target', {

    refresh(frm) {

        calculate_totals(frm);

        // 🔥 Only after submit
        if (frm.doc.docstatus === 1) {

            // ❌ REMOVE old button (no need to write anything — just not adding it)

            // =====================================
            // ✅ DYNAMIC BUTTON BASED ON COMMODITY
            // =====================================

            if (frm.doc.commodity_name === "Wheat") {

                frm.add_custom_button(__('Update Wheat Procurement Progress'), () => {

                    let new_doc = frappe.model.get_new_doc('Update Wheat Procurement Progress');

                    // -------- Parent Fields --------
                    new_doc.procurement_target_id = frm.doc.name;
                    new_doc.state = frm.doc.state;
                    new_doc.kms_year = frm.doc.kms_year;
                    new_doc.season = frm.doc.season;
                    new_doc.scheme = frm.doc.scheme;
                    new_doc.commodity_name = frm.doc.commodity_name;
                    new_doc.procurement_for = frm.doc.procurement_for;
                    new_doc.total_allocated_qty_mt = frm.doc.total_allocated_qty;
                    new_doc.total_no_of_procurement_centers = frm.doc.no_of_procurement_centers;
                    new_doc.msp_per_mt = frm.doc.msp_pmt;

                    // -------- Child Table Copy --------
                    (frm.doc.commodity_details || []).forEach(row => {

                        let child = frappe.model.add_child(
                            new_doc,
                            'Wheat Procurement  Child',   // ⚠️ check exact name
                            'procurement'
                        );

                        child.district = row.district;
                        child.centre = row.centre;
                        target_quantity: flt(row.target_quantity)


                    });

                    frappe.set_route('Form', 'Update Wheat Procurement Progress', new_doc.name);

                }, __('Actions'));
            }


            else if (frm.doc.commodity_name === "Paddy") {

                frm.add_custom_button(__('Update Paddy Procurement Progress'), () => {

    let new_doc = frappe.model.get_new_doc('Update Procurement Progress');

    // Parent fields
    new_doc.procurement_target_id = frm.doc.name;
    new_doc.state = frm.doc.state;
    new_doc.kms_year = frm.doc.kms_year;
    new_doc.season = frm.doc.season;
    new_doc.scheme = frm.doc.scheme;
    new_doc.commodity_name = frm.doc.commodity_name;
    new_doc.procurement_for = frm.doc.procurement_for;
    new_doc.total_allocated_qty_mt = frm.doc.total_allocated_qty;
    new_doc.total_no_of_procurement_centers = frm.doc.no_of_procurement_centers;
    new_doc.msp_per_mt = frm.doc.msp_pmt;

    // Child table (IMPORTANT FIX 👇)
    (frm.doc.commodity_details || []).forEach(row => {

        let child = frappe.model.add_child(
            new_doc,
            'Update Procurement Progress Child',  
            'procurement'
        );

        child.district = row.district;
        child.centre = row.centre;
    });

    frappe.set_route('Form', 'Update Procurement Progress', new_doc.name);

}, __('Actions'));
            }
        }
    }
});


// =====================================
// CHILD EVENTS
// =====================================
frappe.ui.form.on('Procurement Item Child', {

    target_quantity(frm) {
        calculate_totals(frm);
    },

    centre(frm) {
        calculate_totals(frm);
    },

    commodity_details_add(frm) {
        calculate_totals(frm);
    },

    commodity_details_remove(frm) {
        calculate_totals(frm);
    }
});


// =====================================
// TOTAL CALCULATION
// =====================================
function calculate_totals(frm) {

    let total_qty = 0;
    let total_centers = 0;

    (frm.doc.commodity_details || []).forEach(row => {

        total_qty += flt(row.target_quantity);

        // ✅ ADD centres (numeric)
        total_centers += flt(row.centre);
    });

    frm.set_value('total_allocated_qty', total_qty);
    frm.set_value('no_of_procurement_centers', total_centers);
}


// =====================================
// SAFE FLOAT
// =====================================
function flt(val) {
    return parseFloat(val) || 0;
}


 