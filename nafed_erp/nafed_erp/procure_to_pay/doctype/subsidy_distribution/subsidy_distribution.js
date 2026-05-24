// // Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
// // For license information, please see license.txt

// frappe.ui.form.on('Subsidy Distribution', {

//     distribute: function(frm) {

//         let total = frm.doc.total_amount;

//         frm.clear_table("items");

//         let splits = [
//             {type: "Farmer", percent: 75},
//             {type: "Supplier", percent: 20},
//             {type: "NAFED", percent: 5}
//         ];

//         splits.forEach(s => {

//             let row = frm.add_child("items");

//             row.beneficiary_type = s.type;
//             row.amount = (total * s.percent) / 100;

//         });

//         frm.refresh_field("items");

//     }

// });

// frappe.ui.form.on('Subsidy Distribution', {

//     subsidy_request: function(frm) {

//         if (!frm.doc.subsidy_request) return;

//         frappe.db.get_doc('Subsidy Request', frm.doc.subsidy_request)
//             .then(doc => {

//                 frm.clear_table('items');

//                 doc.items.forEach(function(d) {

//                     let row = frm.add_child('items');

//                     row.subsidy_claim = d.subsidy_claim;
//                     row.amount = d.amount;

//                 });

//                 frm.set_value('total_amount', doc.total_amount);
//                 frm.set_value('balance_amount', doc.total_amount);

//                 frm.refresh_field('items');
//             });
//     }
// });
// frappe.ui.form.on('Subsidy Distribution', {

//     paid_amount: function(frm) {

//         let total = frm.doc.total_amount || 0;
//         let paid = frm.doc.paid_amount || 0;

//         if (paid > total) {
//             frappe.msgprint("Paid cannot exceed total");
//             frm.set_value('paid_amount', total);
//             paid = total;
//         }

//         frm.set_value('balance_amount', total - paid);
//     }
// });
frappe.ui.form.on('Subsidy Distribution', {

    distribute_subsidy: function(frm) {

        let total = flt(frm.doc.total_amount);

        if (!total) {
            frappe.msgprint("Total Amount missing");
            return;
        }

        frm.clear_table("subsidy_distribution_item");

        let splits = [
            {type:"Farmer", percent:75},
            {type:"Supplier", percent:20},
            {type:"NAFED", percent:5}
        ];

        splits.forEach(function(d){

            let row = frm.add_child("subsidy_distribution_item");

            row.beneficiary_type = d.type;
            row.amount = (total*d.percent)/100;
            row.payment_status = "Pending";

        });

        frm.refresh_field("subsidy_distribution_item");

        frm.set_value("paid_amount",0);
        frm.set_value("balance_amount",total);

        frappe.msgprint("Distribution created");
    }

});