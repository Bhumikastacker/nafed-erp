frappe.ui.form.on('Subsidy Claim', {

    refresh: function(frm) {

        // Show button after save
        if (!frm.is_new()) {

            frm.add_custom_button('Add to Subsidy Request', function() {

                frappe.model.with_doctype('Subsidy Request', function() {

                    let doc = frappe.model.get_new_doc('Subsidy Request');

                    let row = frappe.model.add_child(
                        doc,
                        'Subsidy Request Item',
                        'items'
                    );

                    row.subsidy_claim = frm.doc.name;
                    row.amount = frm.doc.subsidy_amount;

                    doc.total_amount = frm.doc.subsidy_amount;

                    frappe.set_route(
                        'Form',
                        'Subsidy Request',
                        doc.name
                    );

                });

            }, 'Create');
        }
    },


    // Fetch from Seed Production
    seed_production: function(frm){

        if(!frm.doc.seed_production) return;

        frappe.db.get_doc(
            "Seed Production",
            frm.doc.seed_production
        ).then(doc => {

            frm.clear_table("subsidy_claim_item");

            let total_qty = 0;

            (doc.seed_production_item || []).forEach(function(d){

                let row = frm.add_child(
                    "subsidy_claim_item"
                );

                row.crop = d.crop;
                row.variety = d.variety;

                row.produced_qty = d.produced_qty;
                row.accepted_qty = d.accepted_qty;

                row.eligible_qty = d.accepted_qty;

                row.subsidy_rate =
                    frm.doc.subsidy_rate || 0;

                row.subsidy_amount =
                    row.eligible_qty *
                    row.subsidy_rate;

                total_qty += row.eligible_qty;

            });

            frm.set_value(
                "supplier",
                doc.supplier
            );

    

            frm.set_value(
                "total_eligible_qty",
                total_qty
            );

            frm.refresh_field(
                "subsidy_claim_item"
            );

            calculate_total_subsidy(frm);

        });
    },


    // Recalculate when subsidy rate changes
    subsidy_rate: function(frm){

        (frm.doc.subsidy_claim_item || []).forEach(function(d){

            d.subsidy_rate =
                frm.doc.subsidy_rate || 0;

            d.subsidy_amount =
                (d.eligible_qty || 0) *
                (d.subsidy_rate || 0);

        });

        frm.refresh_field(
            "subsidy_claim_item"
        );

        calculate_total_subsidy(frm);
    }

});


// --------------------
function calculate_total_subsidy(frm){

    let total = 0;

    (frm.doc.subsidy_claim_item || []).forEach(function(d){

        total += d.subsidy_amount || 0;

    });

    frm.set_value(
        "subsidy_amount",
        total
    );
}