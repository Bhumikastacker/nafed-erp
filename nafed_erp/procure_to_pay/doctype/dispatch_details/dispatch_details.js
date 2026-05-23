// // ===============================
// // ✅ CALCULATE TOTAL DELIVERED
// // ===============================
// function calculate_total_delivered(frm) {

//     let total = 0;

//     (frm.doc.delivery_details || []).forEach(row => {
//         total += flt(row.gunny_bags_delivered);
//     });

//     // ✅ Only update if changed
//     if (flt(frm.doc.total_quantity_delivered) !== total) {

//         if (frm.doc.docstatus === 0) {

//             frm.set_value('total_quantity_delivered', total)
//                 .then(() => {
//                     calculate_total_amount(frm);
//                 });

//         } else {

//             if (frm.fields_dict.total_quantity_delivered?.$input) {
//                 frm.fields_dict.total_quantity_delivered.$input.val(total);
//             }

//             calculate_total_amount(frm);
//         }

//     } else {
//         calculate_total_amount(frm);
//     }
// }


// // ===============================
// // ✅ CALCULATE TOTAL AMOUNT
// // ===============================
// function calculate_total_amount(frm) {

//     let qty = flt(frm.doc.total_quantity_delivered || 0);
//     let rate = 0;

//     if (frm.doc.item_details?.length) {
//         rate = flt(frm.doc.item_details[0].unit_price || 0);
//     }

//     let total_amount = qty * rate;

//     // ✅ Only update if changed
//     if (flt(frm.doc.total_amount) !== total_amount) {

//         if (frm.doc.docstatus === 0) {
//             frm.set_value('total_amount', total_amount);
//         } else {
//             if (frm.fields_dict.total_amount?.$input) {
//                 frm.fields_dict.total_amount.$input.val(total_amount);
//             }
//         }
//     }
// }


// // ===============================
// // ✅ FETCH ITEMS INTO SALES INVOICE
// // ===============================
// async function fetch_items_from_single_dispatch(frm, dispatch_name) {

//     frappe.dom.freeze("Fetching Dispatch Items...");

//     try {

//         frm.clear_table("items");

//         let res = await frappe.call({
//             method: "frappe.client.get",
//             args: {
//                 doctype: "Dispatch Details",
//                 name: dispatch_name
//             }
//         });

//         let doc = res.message;
//         let dispatch_qty = flt(doc.total_quantity_delivered || 0);
//         let total_qty = 0;

//         for (let row of (doc.item_details || [])) {

//             let bag = await frappe.call({
//                 method: "frappe.client.get_value",
//                 args: {
//                     doctype: "Jute Bag Item Master",
//                     filters: {
//                         naming_series: row.gunny_bag_name
//                     },
//                     fieldname: [
//                         "wt",
//                         "wt_uom",
//                         "capacity_uom",
//                         "link_service_item",
//                         "commission_percentage"
//                     ]
//                 }
//             });

//             let bag_doc = bag.message || {};
//             let commission = flt(bag_doc.commission_percentage) || 0;

//             let child = frm.add_child("items");

//             child.item_code = bag_doc.link_service_item || row.gunny_bag_name;
//             child.item_name = row.gunny_bag_name;
//             child.qty = 1;
//             total_qty += 1;

//             child.uom = bag_doc.capacity_uom || row.gunny_bag_capacity_uom;

//             child.rate = (dispatch_qty * commission) / 100;
//             child.amount = child.qty * child.rate;
//             child.base_rate = child.rate;
//             child.base_amount = child.amount;

//             child.weight_per_unit = bag_doc.wt || 0;
//             child.weight_uom = bag_doc.wt_uom;
//             child.total_weight = child.qty * (bag_doc.wt || 0);

//             child.dispatch_id = doc.name;
//             child.dispatch_qty = dispatch_qty;
//             child.customer = doc.jute_miller;

//             child.description =
// `Dispatch: ${doc.name}
// Bag: ${row.gunny_bag_name}
// Dispatch Qty: ${dispatch_qty}
// Commission: ${commission}%
// Weight: ${bag_doc.wt || 0} ${bag_doc.wt_uom || ''}`;
//         }

//         frm.set_value("total_qty", total_qty);

//         frm.refresh_field("items");
//         frm.trigger("calculate_taxes_and_totals");

//     } catch (err) {

//         console.error("FULL ERROR:", err);

//         frappe.msgprint({
//             title: "Error",
//             message: err.message || err,
//             indicator: "red"
//         });
//     }

//     frappe.dom.unfreeze();
// }


// // ===============================
// // ✅ DISPATCH DETAILS MAIN
// // ===============================
// frappe.ui.form.on('Dispatch Details', {
//     onload: function(frm) {

//         // ✅ Only calculate in draft
//         if (frm.doc.docstatus === 0) {
//             calculate_total_delivered(frm);
//         }

//         // ✅ Clear Work Order on fresh duplicate
//         // ✅ Clear Work Order ONLY on duplicate (amend)
//         if (frm.is_new() && frm.doc.amended_from) {
//             if (frm.doc.work_order_ref_no) {
//                 frm.set_value("work_order_ref_no", "");

//         frappe.msgprint({
//             message: "Work Order cleared. Please select again.",
//             indicator: "orange"
//         });
//         }
//     }
// },


//     // ===============================
//     // ✅ REFRESH (NO DIRTY ISSUE)
//     // ===============================
//     refresh: async function(frm) {

//         // ❗ Only calculate in draft
//         if (frm.doc.docstatus === 0) {
//             calculate_total_delivered(frm);
//         }

//         if (frm.doc.docstatus === 1) {

//             frm.dashboard.clear_headline();

//             let res = await frappe.db.get_list('Sales Invoice', {
//                 filters: {
//                     custom_jute_dispatch_details: frm.doc.name,
//                     docstatus: ["!=", 2]
//                 },
//                 fields: ['name', 'status', 'docstatus'],
//                 limit: 1
//             });

//             if (res.length > 0) {

//                 let si = res[0];

//                 let color = "blue";
//                 if (si.status === "Paid") color = "green";
//                 else if (si.status === "Unpaid") color = "red";
//                 else if (si.status === "Overdue") color = "orange";
//                 else if (si.docstatus === 0) color = "gray";

//                 let html = `
//                     <span style="color:${color};font-weight:bold;">
//                         Sales Invoice:
//                         <a href="/app/sales-invoice/${si.name}" target="_blank">
//                             ${si.name}
//                         </a>
//                         (${si.status})
//                     </span>
//                 `;

//                 frm.dashboard.set_headline(html);
//                 frm.dashboard.add_indicator(`Invoice: ${si.status}`, color);

//                 // ✅ FIXED LINE
//                 await frappe.call({
//                     method: "frappe.client.set_value",
//                     args: {
//                         doctype: "Dispatch Details",
//                         name: frm.doc.name,
//                         fieldname: "ref",
//                         value: si.name
//                     }
//                 });

//             } else {

//                 frm.dashboard.set_headline(`
//                     <span style="color:gray;font-weight:bold;">
//                         No Sales Invoice
//                     </span>
//                 `);

//                 frm.dashboard.add_indicator('No Invoice', 'gray');

//                 frm.add_custom_button('Create Sales Invoice', () => {

//                     frappe.new_doc('Sales Invoice', {
//                         custom_jute_dispatch_details: frm.doc.name,
//                         custom_jute_work_order: frm.doc.work_order_ref_no,
//                         posting_date: frm.doc.date_of_dispatch,
//                         customer: frm.doc.jute_miller,
//                         custom_department: "jute"
//                     });

//                     setTimeout(async () => {
//                         await fetch_items_from_single_dispatch(cur_frm, frm.doc.name);
//                     }, 800);

//                 }, 'Create');
//             }
//         }
//     },


//     // ===============================
//     // ✅ VALIDATION
//     // ===============================
//     validate: async function(frm) {

//         if (!frm.doc.work_order_ref_no) return;

//         let res = await frappe.call({
//             method: "frappe.client.get_list",
//             args: {
//                 doctype: "Dispatch Details",
//                 filters: {
//                     work_order_ref_no: frm.doc.work_order_ref_no,
//                     name: ["!=", frm.doc.name],
//                     docstatus: ["!=", 2]
//                 },
//                 fields: ["name"],
//                 limit_page_length: 1
//             }
//         });

//         if (res.message && res.message.length > 0) {

//             frappe.throw(
//                 __("Dispatch already exists for Work Order: {0}",
//                 [frm.doc.work_order_ref_no])
//             );
//         }
//     },

//     total_quantity_delivered: function(frm) {
//         calculate_total_amount(frm);
//     }
// });


// // ===============================
// // ✅ ITEM CHILD TABLE
// // ===============================
// frappe.ui.form.on('Gunny Items Child', {

//     unit_price: function(frm) {
//         calculate_total_amount(frm);
//     },

//     item_details_add: function(frm) {
//         calculate_total_amount(frm);
//     },

//     item_details_remove: function(frm) {
//         calculate_total_amount(frm);
//     }
// });


// // ===============================
// // ✅ DELIVERY CHILD TABLE
// // ===============================
// frappe.ui.form.on('Delivery Location Details', {

//     gunny_bags_delivered: function(frm) {
//         calculate_total_delivered(frm);
//     },

//     delivery_details_add: function(frm) {
//         calculate_total_delivered(frm);
//     },

//     delivery_details_remove: function(frm) {
//         calculate_total_delivered(frm);
//     }
// });

// // ===============================
// // AUTO FETCH FROM WORK ORDER
// // ===============================
// function fetch_from_jwo(frm) {

//     if (!frm.doc.work_order_ref_no) return;
//     if (frm.doc.item_details?.length || frm.doc.delivery_details?.length) {
//         return;
//     }


//     frm.clear_table('item_details');
//     frm.clear_table('delivery_details');

//     frappe.model.with_doc('Jute Work Order', frm.doc.work_order_ref_no, function () {

//         let jwo = frappe.model.get_doc('Jute Work Order', frm.doc.work_order_ref_no);

//         // HEADER
//         frm.set_value('date_of_issue', jwo.date_of_issue);
//         frm.set_value('date_of_dispatch', jwo.dispatch_by);
//         frm.set_value('quantity', jwo.total_quantity);

//         // ITEMS
//         (jwo.gunny_bag_details_table || []).forEach(row => {

//             let child = frm.add_child('item_details');

//             Object.assign(child, {
//                 gunny_bag_name: row.gunny_bag_name,
//                 gunny_bag_length_in_cm: row.gunny_bag_length_in_cm,
//                 gunny_bag_width_in_cm: row.gunny_bag_width_in_cm,
//                 gunny_bag_weight: row.gunny_bag_weight,
//                 gunny_bag_uom: row.gunny_bag_uom,
//                 gunny_bag_capacity: row.gunny_bag_capacity,
//                 gunny_bag_capacity_uom: row.gunny_bag_capacity_uom,
//                 unit_price: row.unit_price,
//                 quantity_required: row.quantity_required
//             });

//         });

//         // DELIVERY
//         (jwo.delivery_location_table || []).forEach(row => {

//             let child = frm.add_child('delivery_details');

//             Object.assign(child, {
//                 location_name: row.location_name,
//                 location_address: row.location_address,
//                 location_contact: row.location_contact,
//                 gunny_bags_delivered: 0
//             });

//         });

//         frm.refresh_field('item_details');
//         frm.refresh_field('delivery_details');

//         calculate_total_delivered(frm);
//     });
// }


// // ===============================
// // CALCULATE TOTAL DELIVERED
// // ===============================
// function calculate_total_delivered(frm) {

//     let total = 0;

//     (frm.doc.delivery_details || []).forEach(row => {
//         total += flt(row.gunny_bags_delivered);
//     });

//     if (flt(frm.doc.total_quantity_delivered) !== total) {

//         if (frm.doc.docstatus === 0) {

//             frm.set_value('total_quantity_delivered', total)
//                 .then(() => calculate_total_amount(frm));

//         } else {

//             if (frm.fields_dict.total_quantity_delivered?.$input) {
//                 frm.fields_dict.total_quantity_delivered.$input.val(total);
//             }

//             calculate_total_amount(frm);
//         }

//     } else {
//         calculate_total_amount(frm);
//     }
// }


// // ===============================
// // CALCULATE TOTAL AMOUNT
// // ===============================
// function calculate_total_amount(frm) {

//     let qty = flt(frm.doc.total_quantity_delivered || 0);
//     let rate = 0;

//     if (frm.doc.item_details?.length) {
//         rate = flt(frm.doc.item_details[0].unit_price || 0);
//     }

//     let total_amount = qty * rate;

//     if (flt(frm.doc.total_amount) !== total_amount) {

//         if (frm.doc.docstatus === 0) {
//             frm.set_value('total_amount', total_amount);
//         } else {
//             if (frm.fields_dict.total_amount?.$input) {
//                 frm.fields_dict.total_amount.$input.val(total_amount);
//             }
//         }
//     }
// }


// // ===============================
// // FETCH ITEMS INTO SALES INVOICE
// // ===============================
// async function fetch_items_from_single_dispatch(frm, dispatch_name) {

//     frappe.dom.freeze("Fetching Dispatch Items...");

//     try {

//         frm.clear_table("items");

//         let res = await frappe.call({
//             method: "frappe.client.get",
//             args: {
//                 doctype: "Dispatch Details",
//                 name: dispatch_name
//             }
//         });

//         let doc = res.message;
//         let dispatch_qty = flt(doc.total_quantity_delivered || 0);
//         let total_qty = 0;

//         for (let row of (doc.item_details || [])) {

//             let bag = await frappe.call({
//                 method: "frappe.client.get_value",
//                 args: {
//                     doctype: "Jute Bag Item Master",
//                     filters: {
//                         naming_series: row.gunny_bag_name
//                     },
//                     fieldname: [
//                         "wt",
//                         "wt_uom",
//                         "capacity_uom",
//                         "link_service_item",
//                         "commission_percentage"
//                     ]
//                 }
//             });

//             let bag_doc = bag.message || {};
//             let commission = flt(bag_doc.commission_percentage) || 0;

//             let child = frm.add_child("items");

//             child.item_code =  "Service Item"; // MUST EXIST

//             // child.item_name = row.gunny_bag_name;
//             child.qty = 1;
//             total_qty += 1;

//             child.uom = bag_doc.capacity_uom || row.gunny_bag_capacity_uom;

//             child.rate = (dispatch_qty * commission) / 100;
//             child.amount = child.qty * child.rate;
//             child.base_rate = child.rate;
//             child.base_amount = child.amount;

//             child.weight_per_unit = bag_doc.wt || 0;
//             child.weight_uom = bag_doc.wt_uom;
//             child.total_weight = child.qty * (bag_doc.wt || 0);

//             child.dispatch_id = doc.name;
//             child.dispatch_qty = dispatch_qty;
//             child.customer = doc.jute_miller;

//             child.description =
// `Dispatch: ${doc.name}
// Bag: ${row.gunny_bag_name}
// Dispatch Qty: ${dispatch_qty}
// Commission: ${commission}%
// Weight: ${bag_doc.wt || 0} ${bag_doc.wt_uom || ''}`;
//         }

//         frm.set_value("total_qty", total_qty);

//         frm.refresh_field("items");
//         frm.trigger("calculate_taxes_and_totals");

//     } catch (err) {

//         console.error("FULL ERROR:", err);

//         frappe.msgprint({
//             title: "Error",
//             message: err.message || err,
//             indicator: "red"
//         });
//     }

//     frappe.dom.unfreeze();
// }


// // ===============================
// // MAIN FORM
// // ===============================
// frappe.ui.form.on('Dispatch Details', {

//     onload: function(frm) {

//         if (frm.doc.docstatus === 0) {
//             calculate_total_delivered(frm);
//         }

//         // duplicate case
//         if (frm.is_new() && frm.doc.amended_from) {
//             if (frm.doc.work_order_ref_no) {
//                 frm.set_value("work_order_ref_no", "");
//                 frappe.msgprint({
//                     message: "Work Order cleared. Please select again.",
//                     indicator: "orange"
//                 });
//             }
//         }
//     },

//     // AUTO FETCH TRIGGER
//     work_order_ref_no: function(frm) {

//     if (frm.doc.item_details?.length || frm.doc.delivery_details?.length) {
//         return;
//     }

//     fetch_from_jwo(frm);
// },   



// refresh: async function(frm) {

//     // Draft state calculation
//     if (frm.doc.docstatus === 0) {
//         calculate_total_delivered(frm);
//     }

//     // Only for submitted docs
//     if (frm.doc.docstatus !== 1) return;

//     frm.dashboard.clear_headline();

//     // Fetch existing Sales Invoice
//     let res = await frappe.db.get_list("Sales Invoice", {
//         filters: {
//             custom_jute_dispatch_details: frm.doc.name,
//             docstatus: ["!=", 2]
//         },
//         fields: ["name", "status", "docstatus"],
//         limit: 1
//     });

//     // If invoice exists
//     if (res.length > 0) {

//         let si = res[0];

//         // Status color logic
//         let color = "blue";
//         if (si.status === "Paid") color = "green";
//         else if (si.status === "Unpaid") color = "red";
//         else if (si.status === "Overdue") color = "orange";
//         else if (si.docstatus === 0) color = "gray";

//         // Show dashboard indicator
//         frm.dashboard.add_indicator(`Invoice: ${si.status}`, color);

//         // Prevent refresh loop / blinking
//         if (frm.doc.ref !== si.name) {
//             frm.set_value("ref", si.name);

//             // Save silently only if changed
//             await frm.save_or_update();
//         }

//     } else {

//         // No invoice found
//         frm.dashboard.add_indicator("No Invoice", "gray");

//         // Avoid duplicate button creation
//         if (!frm.custom_buttons["Create Sales Invoice"]) {
//             frm.add_custom_button("Create Sales Invoice", () => {

//                 frappe.new_doc("Sales Invoice", {
//                     custom_jute_dispatch_details: frm.doc.name,
//                     custom_jute_work_order: frm.doc.work_order_ref_no,
//                     posting_date: frm.doc.date_of_dispatch,
//                     customer: frm.doc.jute_miller,
//                     division: "jute"
//                 });

//                 setTimeout(async () => {
//                     await fetch_items_from_single_dispatch(cur_frm, frm.doc.name);
//                 }, 800);

//             }, "Create");
//         }
//     }
// },

//     validate: async function(frm) {

//         if (!frm.doc.work_order_ref_no) return;

//         let res = await frappe.call({
//             method: "frappe.client.get_list",
//             args: {
//                 doctype: "Dispatch Details",
//                 filters: {
//                     work_order_ref_no: frm.doc.work_order_ref_no,
//                     name: ["!=", frm.doc.name],
//                     docstatus: ["!=", 2]
//                 },
//                 fields: ["name"],
//                 limit_page_length: 1
//             }
//         });

//         if (res.message && res.message.length > 0) {
//             frappe.throw(
//                 __("Dispatch already exists for Work Order: {0}",
//                 [frm.doc.work_order_ref_no])
//             );
//         }
//     },

//     total_quantity_delivered: function(frm) {
//         calculate_total_amount(frm);
//     }
// });


// // ===============================
// // ITEM CHILD
// // ===============================
// frappe.ui.form.on('Gunny Items Child', {
//     unit_price: function(frm) {
//         calculate_total_amount(frm);
//     }
// });


// // ===============================
// // DELIVERY CHILD
// // ===============================
// frappe.ui.form.on('Delivery Location Details', {

//     gunny_bags_delivered: function(frm) {
//         calculate_total_delivered(frm);
//     },

//     delivery_details_add: function(frm) {
//         calculate_total_delivered(frm);
//     },

//     delivery_details_remove: function(frm) {
//         calculate_total_delivered(frm);
//     }
// });

// ===============================
// SINGLE ROW RESTRICTION
// ===============================
function restrict_single_row(frm) {
    let grid = frm.get_field("item_details").grid;

    if (grid) {
        grid.cannot_add_rows = true;
        grid.wrapper.find('.grid-add-row').hide();
        grid.wrapper.find('.grid-add-multiple-rows').hide();
    }
}

function enforce_single_row(frm) {
    if (frm.doc.item_details.length > 1) {
        frm.doc.item_details.splice(1);
        frm.refresh_field("item_details");
        frappe.msgprint("Only one row is allowed in Item Details.");
    }
}

// 
// ===============================
// FETCH ITEMS INTO SALES INVOICE
// ===============================
async function fetch_items_from_single_dispatch(frm, dispatch_name) {

    

    frappe.dom.freeze("Fetching Dispatch Items...");

    try {
        frm.clear_table("items");
        

        let res = await frappe.call({
            method: "frappe.client.get",
            args: {
                doctype: "Dispatch Details",
                name: dispatch_name
            }
        });

        

        let doc = res.message;
        let dispatch_qty = flt(doc.total_quantity_delivered || 0);
        let total_qty = 0;

        

        for (let row of (doc.item_details || [])) {



            let bag = await frappe.call({
                method: "frappe.client.get_value",
                args: {
                    doctype: "Jute Bag Item Master",
                    filters: {
                        naming_series: row.gunny_bag_name
                    },
                    fieldname: [
                        "wt",
                        "wt_uom",
                        "capacity_uom",
                        "link_service_item",
                        "commission_percentage"
                    ]
                }
            });

            

            let bag_doc = bag.message || {};
            let commission = flt(bag_doc.commission_percentage) || 0;

            let child = frm.add_child("items");

            let item_code = bag_doc.link_service_item || "Service Item";

            await frappe.model.set_value(child.doctype, child.name, "item_code", item_code);

            child.qty = 1;
            total_qty += 1;

            child.uom = bag_doc.capacity_uom || row.gunny_bag_capacity_uom;

            child.rate = (dispatch_qty * commission) / 100;
            child.amount = child.qty * child.rate;
            child.base_rate = child.rate;
            child.base_amount = child.amount;

            child.weight_per_unit = bag_doc.wt || 0;
            child.weight_uom = bag_doc.wt_uom;
            child.total_weight = child.qty * (bag_doc.wt || 0);

            child.dispatch_id = doc.name;
            child.dispatch_qty = dispatch_qty;
            child.customer = doc.jute_miller;

            child.description =
`Dispatch: ${doc.name}
Bag: ${row.gunny_bag_name}
Dispatch Qty: ${dispatch_qty}
Commission: ${commission}%
Weight: ${bag_doc.wt || 0} ${bag_doc.wt_uom || ''}`;

            
        }

        frm.set_value("total_qty", total_qty);

        frm.refresh_field("items");
        frm.trigger("calculate_taxes_and_totals");

        

    } catch (err) {

        

        frappe.msgprint({
            title: "Error",
            message: err.message || err,
            indicator: "red"
        });
    }

    frappe.dom.unfreeze();
    
}


// ===============================
// FETCH FROM JUTE WORK ORDER
// ===============================
function fetch_from_jwo(frm) {

    

    if (!frm.doc.work_order_ref_no) {
        
        return;
    }

    if (frm.doc.item_details?.length || frm.doc.delivery_details?.length) {
        
        return;
    }

    frm.clear_table('item_details');
    frm.clear_table('delivery_details');

    

    frappe.model.with_doc('Jute Work Order', frm.doc.work_order_ref_no, function () {

        let jwo = frappe.model.get_doc('Jute Work Order', frm.doc.work_order_ref_no);

        

        // HEADER
        frm.set_value('date_of_issue', jwo.date_of_issue);
        frm.set_value('date_of_dispatch', jwo.dispatch_by);
        frm.set_value('quantity', jwo.total_quantity);

        // ITEMS
        let row = (jwo.gunny_bag_details_table || [])[0];

            
        if (row) {

            let child = frm.add_child('item_details');

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
        
    }

        // DELIVERY
        (jwo.delivery_location_table || []).forEach(row => {


            let child = frm.add_child('delivery_details');

            Object.assign(child, {
                location_name: row.location_name,
                location_address: row.location_address,
                location_contact: row.location_contact,
                gunny_bags_req:row.gunny_bags_req,
                gunny_bags_delivered: 0
            });
        });

        frm.refresh_field('item_details');
        frm.refresh_field('delivery_details');

        

        calculate_total_delivered(frm);
    });
}


// ===============================
// CALCULATIONS
// ===============================
function calculate_total_delivered(frm) {

    let total = 0;

    (frm.doc.delivery_details || []).forEach(row => {
        total += flt(row.gunny_bags_delivered);
    });

    

    frm.set_value('total_quantity_delivered', total)
        .then(() => calculate_total_amount(frm));
}


function calculate_total_amount(frm) {

    let qty = flt(frm.doc.total_quantity_delivered || 0);
    let rate = flt(frm.doc.item_details?.[0]?.unit_price || 0);

    let total_amount = qty * rate;

    

    frm.set_value('total_amount', total_amount);
}


// ===============================
// MAIN FORM
// ===============================
frappe.ui.form.on('Dispatch Details', {

    onload: function(frm) {

        

        if (frm.doc.docstatus === 0) {
            calculate_total_delivered(frm);
        }

        if (frm.is_new() && frm.doc.amended_from) {
            
            frm.set_value("work_order_ref_no", "");
        }
    },

    work_order_ref_no: function(frm) {
        
        fetch_from_jwo(frm);
    },

    refresh: async function(frm) {

        

        if (frm.doc.docstatus === 0) {
            calculate_total_delivered(frm);
        }

        if (frm.doc.docstatus !== 1) {
            
            return;
        }

        frm.dashboard.clear_headline();

        let res = await frappe.db.get_list("Sales Invoice", {
            filters: {
                custom_jute_dispatch_details: frm.doc.name,
                docstatus: ["!=", 2]
            },
            fields: ["name", "status"],
            limit: 1
        });

        

        if (res.length > 0) {

            let si = res[0];

            frm.dashboard.add_indicator(`Invoice: ${si.status}`, "blue");

            if (frm.doc.ref !== si.name) {
                frm.set_value("ref", si.name);
                await frm.save_or_update();
            }

        } else {

            

            frm.dashboard.add_indicator("No Invoice", "gray");

            frm.add_custom_button("Create Sales Invoice", () => {

                

                frappe.new_doc("Sales Invoice", {
                    custom_jute_dispatch_details: frm.doc.name,
                    custom_jute_work_order: frm.doc.work_order_ref_no,
                    posting_date: frm.doc.date_of_dispatch,
                    customer: frm.doc.jute_miller,
                    division: "jute"
                });

            }, "Create");
        }
    },

    validate: async function(frm) {

        

        let res = await frappe.call({
            method: "frappe.client.get_list",
            args: {
                doctype: "Dispatch Details",
                filters: {
                    work_order_ref_no: frm.doc.work_order_ref_no,
                    name: ["!=", frm.doc.name]
                },
                limit_page_length: 1
            }
        });

        

        if (res.message?.length) {
            
            frappe.throw(`Dispatch already exists for Work Order: ${frm.doc.work_order_ref_no}`);
        }
    }
});


// ===============================
// CHILD EVENTS
// ===============================
frappe.ui.form.on('Delivery Location Details', {
    gunny_bags_delivered: function(frm) {
        
        calculate_total_delivered(frm);
    }
});


frappe.ui.form.on('Gunny Items Child', {
    item_details_add(frm) {
        enforce_single_row(frm);
    }
});