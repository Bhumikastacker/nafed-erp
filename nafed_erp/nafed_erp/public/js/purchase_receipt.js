function is_created_from_purchase_order(frm) {
    if (!frm.doc.items || frm.doc.items.length === 0) return false;

    return frm.doc.items.some(row => row.purchase_order || row.purchase_order_item);
}
frappe.ui.form.on('Purchase Receipt', {

    custom_whr_no: function(frm) {

        if (!frm.doc.custom_whr_no) return;

        frappe.call({
            method: "frappe.client.get",
            args: {
                doctype: "Dispatch Receipt",
                name: frm.doc.custom_whr_no
            },
            callback: function(r) {

                if (!r.message) return;

                let data = r.message;

                // ===== HEADER FIELDS =====
                frm.set_value("custom_whr_no", data.dispatch_unique_id);
                frm.set_value("posting_date", data.dispatch_date);
                frm.set_value("custom_state", data.state_name);
                frm.set_value("custom_district", data.district_name);
                frm.set_value("custom_state_agency", data.state_agency_name);

                // ⚠️ warehouse field tumhare doctype me nahi hai
                // agar hai to hi use karo
                // frm.set_value("set_warehouse", data.warehouse);

                // ===== CLEAR ITEMS =====
                frm.clear_table("items");

                // ===== ADD SINGLE ROW =====
                let child = frm.add_child("items");

                child.custom_dispatch_id_e_samridhi = data.dispatch_unique_id;
                child.custom_farmer_id_ = data.farmer_id;
                child.custom_farmer_name = data.farmer_name;
                child.custom_total_accepted_bags = data.lot_bags;

                child.qty = data.lot_qty;
                child.received_qty = data.lot_qty;

                child.description = data.packtype;

                // ===== ITEM CODE FETCH =====
                if (data.commodity_name) {

                    frappe.db.get_value(
                        "Item",
                        { item_name: data.commodity_name },
                        "name"
                    ).then(res => {

                        if (res.message) {
                            frappe.model.set_value(child.doctype, child.name, "item_code", res.message.name);
                            frappe.model.set_value(child.doctype, child.name, "item_name", data.commodity_name);
                        } else {
                            frappe.msgprint(`Item not found for Commodity: ${data.commodity_name}`);
                        }

                        frm.refresh_field("items");
                    });

                } else {
                    frm.refresh_field("items");
                }

            }
        });
    },
    custom_warehouse_receipt_no: function(frm) {

        console.log(" Triggered custom_warehouse_receipt_no");

        if (!frm.doc.custom_warehouse_receipt_no) {
            console.log(" No WHR selected");
            return;
        }

        console.log(" Selected WHR:", frm.doc.custom_warehouse_receipt_no);

        frappe.call({
            method: "frappe.client.get",
            args: {
                doctype: "Warehouse Receipt",
                name: frm.doc.custom_warehouse_receipt_no
            },
            callback: function(r) {
                console.log("API Response:", r);

                if (!r.message) {
                    console.log(" No data received from API");
                    return;
                }

                let data = r.message;

                console.log("WHR Data:", data);

               
                frm.set_value("posting_date", data.whr_created_date);
                frm.set_value("custom_state", data.state_name);
                frm.set_value("custom_district", data.district_name);
                frm.set_value("custom_state_agency", data.state_agency_name);
                frm.set_value("set_warehouse", data.warehouse_name);

              
                frm.clear_table("custom_lot_dispatch_details");
                frm.clear_table("custom_lot__details");
                frm.clear_table("items");

                console.log(" Tables cleared");

                if (data.lot_dispatch_details && data.lot_dispatch_details.length) {

                    console.log("Dispatch Rows:", data.lot_dispatch_details.length);

                    data.lot_dispatch_details.forEach(d => {

                        console.log("Dispatch Row:", d);

                        let row = frm.add_child("custom_lot_dispatch_details");

                        row.dispatchid = d.dispatchid;
                        row.vehicle_number = d.vehicle_number;
                        row.delivery_chalan_number = d.delivery_chalan_number;
                        row.dispatch_quantity_in_qtls = d.dispatch_quantity_in_qtls;
                        row.dispatch_bags_count_in_number = d.dispatch_bags_count_in_number;
                        row.dispatch_date = d.dispatch_date;
                        row.farmer_unique_id = d.farmer_unique_id;
                    });

                } else {
                    console.log(" No lot_dispatch_details data");
                }

                if (data.lot_details && data.lot_details.length) {

                    console.log(" Lot Rows:", data.lot_details.length);

                    data.lot_details.forEach(d => {

                        console.log(" Lot Row:", d);
                        let row = frm.add_child("custom_lot__details");

                        row.lot__id = d.lot__id;
                        row.created_date = d.created_date;
                        row.farmer_name = d.farmer_name;
                        row.farmer_unique_id = d.farmer_unique_id;
                        row.bill_number = d.bill_number;
                        row.packaging_type = d.packaging_type;
                        row.quality_parameters_name = d.quality_parameters_name;
                        row.quality_parameters_value = d.quality_parameters_value;
                        row.total_bags = d.total_bags;
                        row.total_quantity_in_quital = d.total_quantity_in_quital;
                        row.total_trade_amount_in_rs = d.total_trade_amount_in_rs;

                    });

                } else {
                    console.log(" No lot_details data");
                }

                let item = frm.add_child("items");

                item.item_code = data.commodity_name || "";
                item.item_name = data.commodity_name || "";
                item.qty = data.total_accepted_quantity_in_qtls || 0;
                item.rate = 0;
                item.custom_total_bags = data.total_accepted_bags_count;

                console.log(" Item row added");

                frm.refresh_fields();

                console.log(" Refresh done");
            }
        });
    },
    
    scan_barcode(frm){

        let code = frm.doc.scan_barcode;

        if (!code) return;

        // clear scanner field
        frm.set_value("scan_barcode","");

        frappe.call({
            method:"nafed_erp.procure_to_pay.doc_events.request_for_quotation.get_item_by_barcode",
            args:{
                barcode: code
            },

            callback: function(r) {

                // ❌ Only block if item is not found
                if (!r.message || !r.message.item_code) {
                    frappe.msgprint("Barcode not found");
                    return;
                }
            
                let item = r.message.item_code;
                let mrp  = flt(r.message.rate); // may be 0 if not present
            
                let rows = frm.doc.items || [];
            
                let existing = rows.find(
                    d => d.item_code === item && d.barcode === code
                );
            
                if (existing) {
            
                    existing.qty += 1;
                    existing.received_qty += 1;
            
                    // ✅ Only set rate if MRP exists
                    if (mrp) {
                        frappe.model.set_value(existing.doctype, existing.name, "rate", mrp);
                        frappe.model.set_value(existing.doctype, existing.name, "price_list_rate", mrp);
                        frappe.model.set_value(existing.doctype, existing.name, "custom_mrp", mrp);
                    }
            
                    frm.refresh_field("items");
                }
                else {
            
                    let empty_row = rows.find(d => !d.item_code);
                    let row = empty_row || frm.add_child("items");
            
                    frappe.model.set_value(row.doctype, row.name, "item_code", item).then(() => {
            
                        frappe.model.set_value(row.doctype, row.name, "barcode", code);
                        frappe.model.set_value(row.doctype, row.name, "received_qty", 1);
                        frappe.model.set_value(row.doctype, row.name, "qty", 1);
            
                        // ✅ Only override if MRP exists
                        if (mrp) {
                            frappe.model.set_value(row.doctype, row.name, "rate", mrp);
                            frappe.model.set_value(row.doctype, row.name, "custom_mrp", mrp);
                            frappe.model.set_value(row.doctype, row.name, "price_list_rate", mrp);
                        }
            
                        frm.refresh_field("items");
                    });
                }
            
                frm.script_manager.trigger("calculate_taxes_and_totals");
            }
        });
    }
});

frappe.ui.form.on("Purchase Receipt", {

    refresh(frm) {

        if (frm.doc.docstatus === 1) {

            frm.add_custom_button(__("REPACK"), function () {

                frappe.route_options = {
                    stock_entry_type: "Repack"
                };

                frappe.new_doc("Stock Entry");

                frappe.after_ajax(() => {

                    setTimeout(() => {

                        let se_frm = cur_frm;

                        // CLEAR DEFAULT EMPTY ROW
                        se_frm.clear_table("items");

                        frm.doc.items.forEach((row, index) => {

                            let child = se_frm.add_child("items");

                            child.item_code = row.item_code;

                            child.qty = row.qty;

                            child.uom = row.uom;

                            child.s_warehouse = frm.doc.set_from_warehouse || row.warehouse;
                            child.t_warehouse = frm.doc.set_warehouse;
                        //  FIRST ROW AS FINISHED GOOD
                            if (index === 0) {

                                child.is_finished_item = 1;

                            }
                        });

                        se_frm.refresh_field("items");

                    }, 1000);

                });

            });

        }

    }

});