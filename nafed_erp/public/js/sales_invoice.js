frappe.ui.form.on('Sales Invoice', {

    refresh: function(frm) {

        toggle_reference_work_order(frm);

        if (frm.doc.docstatus === 0) {

            frm.add_custom_button('Delivery Tracking', async () => {

                let d = new frappe.ui.Dialog({
                    title: "Get Items From Jute Dispatch",
                    size: "large",
                    fields: [
                        {
                            label: "Customer",
                            fieldname: "customer",
                            fieldtype: "Link",
                            options: "Customer",
                            default: frm.doc.customer,
                            reqd: 1,
                            change: async function () {
                                let customer = d.get_value("customer");
                                if (customer) {
                                    await load_dispatch_table(d, customer);
                                }
                            }
                        },
                        {
                            fieldname: "dispatch_html",
                            fieldtype: "HTML"
                        }
                    ],

                    primary_action_label: "Get Items",

                    primary_action: async function () {

                        let selected = get_selected_dispatch(d);

                        if (!selected.length) {
                            frappe.msgprint("Please select at least one Dispatch");
                            return;
                        }

                        let customer = d.get_value("customer");

                        frm.set_value("customer", customer);
                        frm.set_value("division", "jute");

                        frm.__loading_from_button = true;

                        d.hide();

                        await get_items(frm, selected);

                        frm.__loading_from_button = false;
                    }
                });

                d.show();

                if (frm.doc.customer) {
                    await load_dispatch_table(d, frm.doc.customer);
                }

            }, __("Get Items From"));
        }
    },

    division: function(frm) {
        update_division_in_items(frm);
        toggle_reference_work_order(frm);
    },

    custom_jute_dispatch_details: async function(frm) {

        if (frm.__loading_from_button) return;
        if (!frm.doc.custom_jute_dispatch_details) return;

        frm.clear_table("items");

        let res = await frappe.call({
            method: "frappe.client.get",
            args: {
                doctype: "Dispatch Details",
                name: frm.doc.custom_jute_dispatch_details
            }
        });

        let doc = res.message;

        frm.__skip_work_order_trigger = true;

        frm.set_value("customer", doc.jute_miller);
        frm.set_value("custom_jute_work_order", doc.work_order_ref_no);
        frm.set_value("division", "jute");

        frm.__skip_work_order_trigger = false;

        await get_items(frm, [{
            name: doc.name,
            qty: doc.total_quantity_delivered || 0
        }]);
    },

    custom_jute_work_order: async function(frm) {

        if (frm.__loading_from_button) return;
        if (frm.__skip_work_order_trigger) return;
        if (!frm.doc.custom_jute_work_order) return;

        let res = await frappe.call({
            method: "frappe.client.get_list",
            args: {
                doctype: "Dispatch Details",
                filters: {
                    work_order_ref_no: frm.doc.custom_jute_work_order,
                    docstatus: 1
                },
                fields: ["name"],
                order_by: "creation desc",
                limit_page_length: 1
            }
        });

        if (res.message.length) {
            frm.set_value("custom_jute_dispatch_details", res.message[0].name);
        }
    }
});


// =======================
// HELPER FUNCTIONS
// =======================
function get_selected_dispatch(dialog) {

    let selected = [];
    let wrapper = dialog.fields_dict.dispatch_html.$wrapper;

    wrapper.find(".dispatch-check:checked").each(function () {
        selected.push({
            name: $(this).attr("data-name"),
            qty: flt($(this).attr("data-qty"))
        });
    });

    return selected;
}

function update_division_in_items(frm) {
    (frm.doc.items || []).forEach(row => {
        row.division_jute = frm.doc.division;
    });
    frm.refresh_field("items");
}

function toggle_reference_work_order(frm) {
    let show = frm.doc.division === "jute";

    if (frm.fields_dict.items?.grid) {
        frm.fields_dict.items.grid.update_docfield_property(
            "custom_reference_work_order",
            "hidden",
            show ? 0 : 1
        );
    }

    frm.refresh_field("items");
}


// =======================
// LOAD DISPATCH TABLE
// =======================
async function load_dispatch_table(dialog, customer) {

    let wrapper = dialog.fields_dict.dispatch_html.$wrapper;
    wrapper.html("Loading...");

    let dispatch_list = await frappe.call({
        method: "frappe.client.get_list",
        args: {
            doctype: "Dispatch Details",
            filters: { jute_miller: customer, docstatus: 1 },
            fields: [
                "name",
                "total_quantity_delivered",
                "date_of_dispatch",
                "work_order_ref_no"
            ],
            limit_page_length: 500  

        }
    });

    if (!dispatch_list.message.length) {
        wrapper.html("<p>No Dispatch Found</p>");
        return;
    }

    let html = `
        <table class="table table-bordered">
            <thead>
                <tr>
                    <th><input type="checkbox" id="select-all"> Select All</th>
                    <th>Dispatch ID</th>
                    <th>Delivery Date</th>
                    <th>Jute Work Order</th>
                    <th>Dispatch Qty</th>
                    <th>Sales Invoice Status</th>
                </tr>
            </thead>
            <tbody>
    `;

    for (let d of dispatch_list.message) {

        let dispatch_qty = flt(d.total_quantity_delivered || 0);

        let si = await frappe.call({
            method: "frappe.client.get_list",
            args: {
                doctype: "Sales Invoice",
                filters: {
                    docstatus: ["!=", 2],
                    custom_jute_dispatch_details: d.name
                },
                fields: ["name"],
                limit_page_length: 1
            }
        });

        let is_created = si.message.length;

        let si_status = is_created
            ? `<span style="color:green;">Created (${si.message[0].name})</span>`
            : `<span style="color:red;">Not Created</span>`;

        let disabled = is_created ? "disabled" : "";

        html += `
            <tr>
                <td>
                    <input type="checkbox" class="dispatch-check"
                        ${disabled}
                        data-name="${d.name}"
                        data-qty="${dispatch_qty}">
                </td>
                <td>${d.name}</td>
                <td>${d.date_of_dispatch || ""}</td>
                <td>${d.work_order_ref_no || ""}</td>
                <td>${dispatch_qty}</td>
                <td>${si_status}</td>
            </tr>
        `;
    }

    html += `</tbody></table>`;
    wrapper.html(html);

    wrapper.find("#select-all").on("change", function () {
        let checked = $(this).is(":checked");
        wrapper.find(".dispatch-check:not(:disabled)").prop("checked", checked);
    });
}


// ============================================
// FINAL FETCH (FIXED)
// ============================================
// 
async function get_items(frm, selected_dispatches) {

    if (frm.__fetching_items) return;
    frm.__fetching_items = true;

    console.log("START get_items");
    console.log("Selected Dispatches:", selected_dispatches);

    frappe.dom.freeze("Fetching Items...");

    try {
        frm.clear_table("items");

        let total_qty = 0;

        for (let d of selected_dispatches) {

            console.log("Processing Dispatch:", d.name);

            let res = await frappe.call({
                method: "frappe.client.get",
                args: { doctype: "Dispatch Details", name: d.name }
            });

            let doc = res.message;
            let dispatch_qty = flt(doc.total_quantity_delivered || 0);

            console.log("Dispatch Data:", doc);
            console.log("Dispatch Qty:", dispatch_qty);

            for (let row of (doc.item_details || [])) {

                console.log("Item Row:", row);

                let bag = await frappe.call({
                    method: "frappe.client.get_value",
                    args: {
                        doctype: "Jute Bag Item Master",
                        filters: {
                            name: row.gunny_bag_name
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

                console.log(" Bag Doc:", bag_doc);

                let commission = flt(bag_doc.commission_percentage) || 0;
                let unit_price = flt(row.unit_price || 0);

                console.log(" Commission %:", commission);
                console.log("Unit Price:", unit_price);

                
                let rate = (dispatch_qty * unit_price * commission) / 100;

                console.log("RATE CALCULATION =>", {
                    dispatch_qty,
                    unit_price,
                    commission,
                    formula: "(dispatch_qty * unit_price * commission) / 100",
                    rate
                });

                let child = frm.add_child("items");

                let item_code = bag_doc.link_service_item || "Service Item";

                console.log("Item Code:", item_code);

               await frappe.model.set_value(child.doctype, child.name, "item_code", item_code);

                // rate = (dispatch_qty * commission) / 100;

                child.qty = 1;
                total_qty += 1;

                child.uom = bag_doc.capacity_uom || row.gunny_bag_capacity_uom;

                child.rate = rate;
                child.price_list_rate = rate;        
                child.base_rate = rate;

                child.amount = child.qty * rate;
                child.base_amount = child.amount;

                console.log("AMOUNT =>", {
                    qty: child.qty,
                    rate: child.rate,
                    amount: child.amount
                });

                child.dispatch_id = doc.name;
                child.dispatch_qty = dispatch_qty;
                child.customer = doc.jute_miller;
                child.custom_reference_work_order = doc.work_order_ref_no || "";
                child.division_jute = frm.doc.division;

                child.weight_per_unit = bag_doc.wt || 0;
                child.weight_uom = bag_doc.wt_uom;
                child.total_weight = bag_doc.wt || 0;

                child.description = `Dispatch: ${doc.name}
Bag: ${row.gunny_bag_name}
Total Dispatch Qty: ${dispatch_qty}
Commission: ${commission}%
Amount: ${rate}`;

                
            }
        }

        console.log("TOTAL ITEMS QTY:", total_qty);

        frm.set_value("total_qty", total_qty);

        toggle_reference_work_order(frm);
        frm.refresh_field("items");
        frm.trigger("calculate_taxes_and_totals");

        
    } catch (err) {
        
        frappe.msgprint("Error fetching items");
    }

    frappe.dom.unfreeze();
    frm.__fetching_items = false;
}