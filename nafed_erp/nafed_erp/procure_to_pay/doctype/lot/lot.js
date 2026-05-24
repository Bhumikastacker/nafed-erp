// Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on("Lot", {
    refresh(frm) {

        if (!frm.is_new()) {

            frm.add_custom_button("Create Lot Dispatch", function () {

                let dispatch_doc = frappe.model.get_new_doc("Lot Dispatch");

                // BASIC IDENTIFICATION
                dispatch_doc.dispatch_date = frappe.datetime.nowdate();
                dispatch_doc.division = frm.doc.division;
                dispatch_doc.season = frm.doc.season;
                dispatch_doc.commodity = frm.doc.commodity;
                dispatch_doc.center = frm.doc.center;
                dispatch_doc.state_agency = frm.doc.state_agency;
                // LOCATION / ORGANIZATION
                dispatch_doc.society = frm.doc.society;
                dispatch_doc.center = frm.doc.center;
                dispatch_doc.state = frm.doc.state;
                dispatch_doc.district = frm.doc.district;
                dispatch_doc.lot_id = frm.doc.name
                // FARMER & LOT LINKING TABLE
                let row = frappe.model.add_child(dispatch_doc, "Lot Details", "lot_details");
                row.farmer_id = frm.doc.farmer_id;
                row.lot_id = frm.doc.name;
                row.lot_quantity = frm.doc.lot_qty;
                row.lot_bags = frm.doc.lot_bags;

                // DISPATCH SUMMARY
                dispatch_doc.dispatch_quantity = frm.doc.lot_qty;
                dispatch_doc.dispatch_bags = frm.doc.lot_bags;

                frappe.set_route("Form", "Lot Dispatch", dispatch_doc.name);

            }, "Create");

        }

    }
});