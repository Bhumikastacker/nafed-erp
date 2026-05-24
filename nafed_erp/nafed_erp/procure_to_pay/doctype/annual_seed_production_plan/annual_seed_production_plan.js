// Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on('Annual Seed Production Plan', {

    refresh: function(frm) {

        if (frm.doc.name && frm.doc.name.startsWith("ASP-")) {
            frm.set_value("annual_production_plan_id", frm.doc.name);
        }

    }

});

frappe.ui.form.on('Annual Seed Production Plan', {

    get_government_request: function(frm) {

        frappe.prompt([
            {
                label: 'Government Request',
                fieldname: 'government_request',
                fieldtype: 'Link',
                options: 'Government Request',
                reqd: 1
            }
        ], function(values) {

            frappe.db.get_doc('Government Request', values.government_request)
                .then(doc => {

                    console.log("FULL DOC:", doc);

                    // ✅ FETCH PARENT FIELDS
                    frm.set_value('plan_year', doc.plan_year);
                    frm.set_value('requesting_date', doc.requesting_date);
                    frm.set_value('gov_request_id', doc.gov_request_id);

                    // 🔄 CLEAR TABLE
                    frm.clear_table("government_request_item");

                    let items = doc.item_details || [];

                    if (!items.length) {
                        frappe.msgprint("No items found in selected Government Request");
                        return;
                    }

                    items.forEach(function(d) {

                        let row = frm.add_child("government_request_item");

                        row.state = d.state;
                        row.crop = d.crop;
                        row.variety = d.variety;
                        row.quantity = d.quantity;

                    });

                    frm.refresh_field("government_request_item");

                    frappe.show_alert("Items fetched successfully");

                });

        }, 'Select Government Request');

    }

});

frappe.ui.form.on('Annual Seed Production Plan', {
    generate_breeder: function(frm) {
        generateRows(frm, 'breeder_seed_plan_item', 'Breeder');
    },

    generate_foundation: function(frm) {
        generateRows(frm, 'foundation_seed_plan_item', 'Foundation');
    },

    generate_certified: function(frm) {
        generateRows(frm, 'certified_seed_plan_item', 'Certified');
    }

});

// This function works for any of the three tables
function generateRows(frm, tableFieldname, type) {
    // Check if the table field exists on the form
    if (!frm.fields_dict[tableFieldname]) {
        frappe.msgprint(__("Table field '{0}' not found. Please add it to the form layout.", [tableFieldname]));
        return;
    }
    
    frappe.prompt([
        {fieldname: 'crop', fieldtype: 'Link', label: 'Crop', options: 'Crop', reqd: 1},
        {fieldname: 'season', fieldtype: 'Link', label: 'Season', options: 'Season', reqd: 1},
        {fieldname: 'start_year', fieldtype: 'Int', label: 'Start Year', reqd: 1},
        {fieldname: 'end_year', fieldtype: 'Int', label: 'End Year', reqd: 1}
    ], function(values) {
        const ageGroups = ['0 to 5 Years', '5 to 10 Years', '>10 Years'];
        const variants = ['V1', 'V2', 'V3', 'V4'];
        
        frm.clear_table(tableFieldname);
        
        for (let year = values.start_year; year <= values.end_year; year++) {
            for (let age of ageGroups) {
                for (let variant of variants) {
                    let row = frm.add_child(tableFieldname);
                    row.crop = values.crop;
                    row.year = year;
                    row.season = values.season;
                    row.age_varieties = age;
                    row.varient = variant;
                    row.target_physical = 0;
                    row.target_financial = 0;
                    row.achievement_physical = 0;
                    row.achievement = 0;
                }
            }
        }
        
        frm.refresh_field(tableFieldname);
        let totalRows = (values.end_year - values.start_year + 1) * ageGroups.length * variants.length;
        frappe.msgprint(__('Generated {0} rows for {1} seed – crop {2}, season {3}, years {4}-{5}',
            [totalRows, type, values.crop, values.season, values.start_year, values.end_year]));
    }, 'Generate ' + type + ' Seed Rows', 'Generate');
}

frappe.ui.form.on('Annual Seed Production Plan', {

    refresh: function(frm) {

        // Show only after save
        // if (!frm.is_new()) {

            // Optional: show only after submit
            if (frm.doc.docstatus === 1) {

            frm.add_custom_button(__('Create Supplier Request'), function() {

                create_supplier_request(frm);

            }, __('Create'));  // 👈 appears near Submit under "Create"
        }
    }

});


function create_supplier_request(frm) {

    if (!frm.doc.government_request_item?.length) {
        frappe.msgprint("No items found in Annual Plan");
        return;
    }

    frappe.prompt([
        {
            label: 'Supplier',
            fieldname: 'supplier',
            fieldtype: 'Link',
            options: 'Supplier',
            reqd: 1
        }
    ], function(values) {

        let total = frm.doc.government_request_item.length;
        let created = 0;

        frm.doc.government_request_item.forEach(function(item) {

            frappe.call({
                method: "frappe.client.insert",
                args: {
                    doc: {
                        doctype: "Supplier Production Plan Request",
                        supplier: values.supplier,
                        gov_request_id:frm.doc.gov_request_id,
                        annual_plan: frm.doc.name,
                        state: item.state,
                        crop: item.crop,
                        variety: item.variety,
                        requested_quantity: item.quantity,
                        season: frm.doc.season,
                        request_date: frappe.datetime.nowdate(),
                        status: "Draft"
                    }
                },
                callback: function() {
                    created++;

                    if (created === total) {
                        frappe.msgprint("All Supplier Requests Created Successfully");
                    }
                }
            });

        });

    });
}

frappe.ui.form.on('Annual Seed Production Plan', {
    refresh: function(frm) {
        if (frm.doc.docstatus === 1) {
            frm.add_custom_button('Create Govt Action Plan', function() {
                create_action_plan(frm);
            }, 'Create');
        }
    }
});
function create_action_plan(frm) {

    frappe.model.with_doctype('Government Action Plan', function() {

        let doc = frappe.model.get_new_doc('Government Action Plan');

        doc.annual_plan = frm.doc.name;
        doc.plan_year = frm.doc.plan_year;
        doc.approval_date = frappe.datetime.nowdate();
        doc.status = "Draft";

        (frm.doc.government_request_item || []).forEach(function(item) {

            let row = frappe.model.add_child(
                doc,
                'Government Action Plan Item',
                'government_action_plan_item'   // ✅ KEEP THIS ONLY
            );

            // row.state = item.state;
            // row.crop = item.crop;
            // row.variety = item.variety;
            // row.quantity = item.quantity;

        });

        frappe.set_route('Form', 'Government Action Plan', doc.name);
    });
}
frappe.ui.form.on('Government Action Plan', {
    refresh: function(frm) {

        if (frm.doc.docstatus === 1) {  // only after submit

            frm.add_custom_button('Create Supplier Allocation', function() {
                create_allocation(frm);
            }, 'Create');

        }
    }
});
function create_allocation(frm) {

    frappe.prompt([
        {
            label: 'Supplier',
            fieldname: 'supplier',
            fieldtype: 'Link',
            options: 'Supplier',
            reqd: 1
        }
    ], function(values) {

        frappe.model.with_doctype('Supplier Allocation', function() {

            let doc = frappe.model.get_new_doc('Supplier Allocation');

            doc.action_plan = frm.doc.name;
            doc.annual_plan = frm.doc.annual_plan;
            doc.supplier = values.supplier;
            doc.allocation_date = frappe.datetime.nowdate();
            doc.status = "Draft";

            (frm.doc.government_action_plan_item || []).forEach(function(item) {

                let row = frappe.model.add_child(
                    doc,
                    'Supplier Allocation Item',
                    'supplier_allocation_item'   // ⚠️ verify this exists
                );

                row.crop = item.crop;
                row.variety = item.variety;
                row.approved_qty = item.quantity;
                row.allocated_qty = item.quantity;
                row.remaining_qty = 0;

            });

            frappe.set_route('Form', 'Supplier Allocation', doc.name);
        });

    });
}