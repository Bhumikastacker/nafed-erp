frappe.ui.form.on("Material Request", {
    refresh(frm) {


        // SUBCONTRACTING FLOW → PURCHASE ORDER
        if (frm.doc.custom_subcontracting) {
            frm.remove_custom_button("Purchase Order", "Create");
            frm.add_custom_button("Create Purchase Order", function () {

                frappe.model.open_mapped_doc({
                    method: "nafed_erp.production.doc_events.material_request.make_subcontracting_po",
                    frm: frm
                });

            }, __("Create"));
        }

        // INHOUSE FLOW → PRODUCTION PLAN
        if (!frm.doc.custom_subcontracting) {

            frm.add_custom_button("Create Production Plan", async function () {

                for (let row of frm.doc.items) {

                    let bom_res = await frappe.db.get_value(
                        "BOM",
                        {
                            item: row.item_code,
                            is_active: 1,
                            is_default: 1
                        },
                        "name"
                    );

                    if (!bom_res.message?.name) {
                        frappe.throw(
                            `No Active Default BOM found for Item: ${row.item_code}`
                        );
                    }
                }

                let pp = frappe.model.get_new_doc("Production Plan");

                pp.company = frm.doc.company;
                pp.get_items_from = "Material Request";

                let mr_row = frappe.model.add_child(
                    pp,
                    "Production Plan Material Request",
                    "material_requests"
                );

                mr_row.material_request = frm.doc.name;
                mr_row.material_request_date = frm.doc.transaction_date;

                frappe.set_route("Form", "Production Plan", pp.name);

            }, __("Create"));
        }
        }
});


frappe.ui.form.on("Material Request", {

    refresh(frm) {

        // Only for new document
        if (!frm.is_new()) {
            return;
        }
         // Skip Administrator
        if (frappe.session.user === "Administrator") {
            return;
        }


        if (!frappe.user.has_role("POS division User")) {
            return;
        }

        frm.set_value(
            "material_request_type",
            "Material Transfer"
        );
         frm.set_df_property(
                "material_request_type",
                "read_only",
                1
            );

        frappe.call({

            method: "nafed_erp.procure_to_pay.api.pos_profile.get_pos_profile_details",

            callback: function(r) {

                if (!r.message) {
                    return;
                }

                // TARGET WAREHOUSE
                frm.set_value(
                    "set_warehouse",
                    r.message.warehouse
                );

                // SOURCE WAREHOUSE
                frm.set_value(
                    "set_from_warehouse",
                    r.message.target_warehouse
                );

                // STORE / BRANCH
                frm.set_value(
                    "custom_branch_",
                    r.message.store
                );
            }
        });
    }
});
