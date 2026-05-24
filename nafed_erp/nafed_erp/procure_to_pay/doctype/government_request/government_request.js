// Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
// For license information, please see license.txt

// frappe.ui.form.on('Government Request', {
//     refresh: function(frm) {

//         // Show button only after saving document
//         if (frm.doc.docstatus === 1) {

//             frm.add_custom_button('Create RFQ', function() {

//                 frappe.model.open_mapped_doc({
//                     method: "nafed_erp.procure_to_pay.doctype.government_request.government_request.make_rfq",
//                     frm: frm
//                 });

//             }, 'Create');

//         }
//     }
// });
frappe.ui.form.on('Government Request', {

    refresh: function(frm) {

        if (frm.doc.name && frm.doc.name.startsWith("GR-")) {
            frm.set_value("gov_request_id", frm.doc.name);
        }

    }

});


