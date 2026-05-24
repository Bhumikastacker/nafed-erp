// frappe.ui.form.on("Supplier", {
//     custom_is_farmer(frm) {
//         if (frm.doc.custom_is_farmer == 1) {
//             frm.set_value("custom_is_sla", 0);
//             frm.set_value("custom_other", 0);

//             frm.set_df_property("supplier_name", "label", "Farmer Name");
//             frm.set_df_property("custom_farmer_registration_date", "label", "Farmer Registration Date")
//             frm.set_df_property("custom_date_of_birth", "label", "Date Of Birth")
//             frm.set_df_property("custom_sla", "label", "Service Level Agreement")
//             frm.set_df_property("supplier_group", "label", "Farmer category")

//         } else {
//             frm.set_df_property("supplier_name", "label", "SLA Name");
//             frm.set_df_property("custom_farmer_registration_date", "label", "SLA Registration Date")
//             frm.set_df_property("supplier_group", "label", "SLA category")


//         }


//         frm.set_query("custom_sla", function () {
//             return {
//                 "filters": { "custom_is_sla": 1 }

//             };
//         })
//     },

//     custom_is_sla(frm) {
//         if (frm.doc.custom_is_sla == 1) {
//             frm.set_value("custom_is_farmer", 0);
//             frm.set_value("custom_other", 0);

//         }

//         frm.set_query("custom_sla", function () {
//             return {
//                 "filters": { "custom_is_farmer": 1 }

//             };
//         })
//     },
//     refresh(frm) {

//         // hidding fields for all roles
//         [
//             "is_transporter"
//         ].map((field) => frm.set_df_property(field, "hidden", 1));
//         // ["last_name","email"].map((field) => frm.set_df_property(field, "reqd", 1));

//         if (frm.doc.custom_is_sla == 1) {
//             frm.set_value("custom_is_farmer", 0);
//             frm.set_value("custom_other", 0);
//             frm.set_df_property("supplier_name", "label", "SLA Name");
//             frm.set_df_property("custom_farmer_registration_date", "label", "SLA Registration Date")
//             frm.set_df_property("custom_date_of_birth", "label", "Date Of Incorporation")
//             frm.set_df_property("custom_sla", "label", "Farmer")
//             frm.set_df_property("supplier_group", "label", "SLA category")


//         } else {
//             frm.set_df_property("supplier_name", "label", "SLA Name");
//             frm.set_df_property("custom_farmer_registration_date", "label", "SLA Registration Date")
//             frm.set_df_property("custom_date_of_birth", "label", "Date Of Birth")
//             frm.set_df_property("custom_sla", "label", "Farmer")
//             frm.set_df_property("supplier_group", "label", "SLA category")

//         }
//         frm.set_query("custom_sla", function () {
//             return {
//                 "filters": { "custom_is_farmer": 1 }

//             };
//         })
//         frm.set_query("supplier_group", function () {
//             return {
//                 "filters": {}

//             };
//         })
//     },
//     custom_other(frm) {
//         if (frm.doc.custom_other == 1) {
//             frm.set_value("custom_is_farmer", 0);
//             frm.set_value("custom_is_sla", 0);


//         }

//     },

//     validate(frm) {
//         if (frm.doc.custom_is_sla && frm.doc.custom_is_farmer) {
//             frappe.throw("Only one option allowed (SLA or Farmer)");
//         }

//         if (!frm.doc.custom_is_sla && !frm.doc.custom_is_farmer) {
//             frappe.throw("Please select one option (SLA or Farmer)");
//         }
//     }

// });


// -------------------------------------------------------------------------------------

frappe.ui.form.on("Supplier", {
    // Initial setup when the form is loaded
    onload(frm) {
        if (frm.is_new()) {
            // Defaulting to 0 when creating a new Supplier
            frm.set_value("custom_is_sla", 0);
            frm.set_value("custom_is_farmer", 0);
            frm.set_value("custom_other", 0);
        }
    },

    // Trigger for GST mandatory logic when category is changed
    gst_category(frm) {
        frm.trigger("manage_document_mandatories");
    },

    // --- START: LABEL AND MANDATORY LOGIC FOR DETAILS TAB ---
    setup_fields_visibility(frm) {
        // Sabse pehle saare fields ko default non-mandatory (0) kar dete hain
        const fields_to_reset = ["supplier_name", "supplier_group", "supplier_type"];
        fields_to_reset.forEach(f => frm.set_df_property(f, "reqd", 0));

        // [SECTION: OTHER]
        if (frm.doc.custom_other == 1) {
            frm.set_df_property("supplier_name", "label", "Supplier Name");
            frm.set_df_property("supplier_group", "label", "Supplier Group");
            // Mandatory status 0 hi rahega (Requirement change)
        } 
        // [SECTION: IS FARMER]
        else if (frm.doc.custom_is_farmer == 1) {
            frm.set_df_property("supplier_name", "label", "Farmer Name");
            frm.set_df_property("supplier_group", "label", "Farmer category");
        } 
        // [SECTION: IS SLA]
        else {
            frm.set_df_property("supplier_name", "label", "SLA Name");
            frm.set_df_property("supplier_group", "label", "SLA category");
        }
    },

    // --- START: DOCUMENT MANDATORY LOGIC FOR DOCUMENTS TAB ---
    manage_document_mandatories(frm) {
        const all_doc_fields = [
            "custom_msme_certificate", "custom_pan_card", "custom_gst_certificate",
            "custom_aadhar_card", "custom_aadhar_card_number",
            "custom_license_copy", "custom_past_experience",
            "custom_fssai_licenseif_applicable"
        ];

        // Sabse pehle saare documents ko non-mandatory (0) kar do
        all_doc_fields.forEach(field => frm.set_df_property(field, "reqd", 0));

        // Note: Yahan pe pehle Farmer/SLA ke liye kuch fields ko 1 kiya ja raha tha,
        // jise ab hata diya gaya hai taaki kuch bhi mandatory na rahe.
        
        // Agar future mein SLA ke liye PAN mandatory karna ho, tabhi yahan code likhna.
        // Filhaal sab 0 hai.
    },

    // --- MUTUALLY EXCLUSIVE CHECKBOX LOGIC ---
    custom_is_farmer(frm) {
        if (frm.doc.custom_is_farmer == 1) {
            frm.set_value("custom_is_sla", 0);
            frm.set_value("custom_other", 0);
        }
        frm.trigger("setup_fields_visibility");
        frm.trigger("manage_document_mandatories");
    },

    custom_is_sla(frm) {
        if (frm.doc.custom_is_sla == 1) {
            frm.set_value("custom_is_farmer", 0);
            frm.set_value("custom_other", 0);
        }
        frm.trigger("setup_fields_visibility");
        frm.trigger("manage_document_mandatories");
    },

    custom_other(frm) {
        if (frm.doc.custom_other == 1) {
            frm.set_value("custom_is_farmer", 0);
            frm.set_value("custom_is_sla", 0);
        }
        frm.trigger("setup_fields_visibility");
        frm.trigger("manage_document_mandatories");
    },

    refresh(frm) {
        // Standard field hide karna
        ["is_transporter"].map((field) => frm.set_df_property(field, "hidden", 1));
        frm.trigger("setup_fields_visibility");
        frm.trigger("manage_document_mandatories");
    },

    // --- FORM VALIDATION ---
    validate(frm) {
        let selected_count = (frm.doc.custom_is_sla || 0) + (frm.doc.custom_is_farmer || 0) + (frm.doc.custom_other || 0);

        if (selected_count > 1) {
            frappe.throw("Only one option allowed (SLA, Farmer, or Other)");
        }
        // if (selected_count === 0) {
        //     frappe.throw("Please select at least one option (SLA, Farmer, or Other)");
        // }
    }
});