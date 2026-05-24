frappe.ui.form.on("PF Investment", {
    refresh(frm) {

        set_total_amount(frm);
    
        // ==========================================================
        // Hide "Add Row" in maturity table
        // ==========================================================
        frm.get_field("maturity_details_table").grid.cannot_add_rows = true;
        frm.refresh_field("maturity_details_table");
    
        // ==========================================================
        // Only for Submitted Docs
        // ==========================================================
        if (frm.doc.docstatus !== 1) return;
    
        // ==========================================================
        // 1️⃣ Payment Entry Button (your existing)
        // ==========================================================
        frm.add_custom_button(__("Payment Entry"), () => {
            frappe.call({
                method: "nafed_erp.pf_trust.doctype.pf_investment.pf_investment.make_payment_entry_from_pf_investment",
                args: { source_name: frm.doc.name },
                callback: (r) => {
                    if (r.message) {
                        frappe.model.sync(r.message);
                        frappe.set_route("Form", r.message.doctype, r.message.name);
                    }
                }
            });
        }, __("Create"));
    
        // ==========================================================
        // 2️⃣ Journal Entry Button (ONLY if Main JV not exists)
        // ==========================================================
        frappe.db.get_list("Journal Entry", {
            filters: {
                custom_pf_investment: frm.doc.name,
                custom_jv_type: "Main",
                docstatus: 1
            },
            fields: ["name"],
            limit: 1
        }).then(res => {
    
            if (!res.length) {
    
                frm.add_custom_button(__("Journal Entries"), () => {
                    frappe.call({
                        method: "nafed_erp.pf_trust.doctype.pf_investment.pf_investment.create_all_journal_entries",
                        args: { docname: frm.doc.name },
                        freeze: true,
                        freeze_message: __("Creating Journal Entries...")
                    }).then(r => {
                        if (r.message) {
    
                            let msg = `Main JV: ${r.message.main_jv}`;
    
                            if (r.message.interest_jvs.length) {
                                msg += `<br><br>Interest JVs:<br>${r.message.interest_jvs.join("<br>")}`;
                            }
    
                            frappe.msgprint(msg);
    
                            // refresh form to hide button after creation
                            frm.reload_doc();
                        }
                    });
                }, __("Create"));
            }
    
            // ======================================================
            // 3️⃣ View Journal Entries (ALWAYS)
            // ======================================================
            frm.add_custom_button(__("View Journal Entries"), () => {
                frappe.set_route("List", "Journal Entry", {
                    custom_pf_investment: frm.doc.name
                });
            }, __("View"));
    
        });
    },
    
face_value(frm) {
    set_total_amount(frm);
    generate_interest_table(frm);
},

interest_paid(frm) {
    set_total_amount(frm);
},

rate(frm) {
    generate_interest_table(frm);
},

first_interest_date(frm) {
    generate_interest_table(frm);
},

interest_frequency(frm) {
    generate_interest_table(frm);
},

day_base_calculation(frm) {
    generate_interest_table(frm);
},

    //=================================================================================
    // 2. New Change to automatically generate rows when the Interest Mode is selected.
    // ================================================================================
  interest_mode: function(frm) {
    if (frm.doc.interest_mode) {

        // Clear the previous rows
        frm.clear_table("maturity_details_table");

        let rows_to_add = 0;
        const mode = frm.doc.interest_mode;
        
        if (mode == "Yearly") rows_to_add = 1;
        else if (mode == "Half Yearly") rows_to_add = 2;
        else if (mode == "Quarterly") rows_to_add = 4;
        else if (mode == "Monthly") rows_to_add = 12;

        // Iterate through a loop to add rows to the child table
        for (let i = 0; i < rows_to_add; i++) {
            frm.add_child("maturity_details_table");
        }
        
        // Refresh the UI so that the rows become visible
        frm.refresh_field("maturity_details_table");
    }
  },

  onload(frm) {
    set_investment_company_query(frm);
    set_investment_category_company_query(frm);
  }
});

function set_total_amount(frm) {

    const face = flt(frm.doc.face_value);
    const interest = flt(frm.doc.interest_paid);
    frm.set_value("total_amount", face + interest);
}


        // Show button only when document is submitted and has no jv reference 
        // if (frm.doc.docstatus === 1 && !frm.doc.journal_entry) {

        //     frm.add_custom_button("Journal Entry", function() {

        //         frappe.call({
        //             method: "nafed_erp.pf_trust.doctype.pf_investment.pf_investment.create_journal_entry",
        //             args: {
        //                 docname: frm.doc.name
        //             },
        //             freeze: true,
        //             freeze_message: __("Creating Journal Entry...")
        //         }).then(r => {

        //             if (r.message) {
        //                 frappe.msgprint("Journal Entry Created: " + r.message);

        //                 // Redirect to Journal Entry
        //                 frappe.set_route("Form", "Journal Entry", r.message);
        //             }

        //         });

        //     }, __("Create"));
        // }
    


frappe.ui.form.on("Maturity Details", {
    maturity_percentage: function(frm, cdt, cdn) {
        calculate_child_maturity(frm, cdt, cdn);
    }
});

function calculate_child_maturity(frm, cdt, cdn) {
    let row = locals[cdt][cdn];

    if (!frm.doc.maturity_amount || !row.maturity_percentage) {
        row.maturity_amount = 0;
    } else {
        row.maturity_amount = 
            (frm.doc.maturity_amount * row.maturity_percentage) / 100;
    }

    frm.refresh_field("maturity_details_table");
}


function set_investment_company_query(frm) {
    frm.set_query("investment", function() {

        if (!frm.doc.company) {
            frappe.msgprint("Please select Company first");
            return;
        }

        return {
            filters: {
                company: frm.doc.company
            }
        };
    });
}
function set_investment_category_company_query(frm) {
    frm.set_query("investment_category", function() {

        if (!frm.doc.company) {
            frappe.msgprint("Please select Company first");
            return;
        }

        return {
            filters: {
                company: frm.doc.company
            }
        };
    });
}
function generate_interest_table(frm) {
    console.log("Interest schedule triggered");
    if (!frm.doc.face_value ||
        !frm.doc.rate ||
        !frm.doc.first_interest_date ||
        !frm.doc.interest_frequency) {
        return;
    }



    frappe.call({
        method: "nafed_erp.pf_trust.doctype.pf_investment.pf_investment.generate_interest_schedule",
        args: {
            doc: JSON.stringify(frm.doc)
        },
        callback: function (r) {

            if (!r.message) return;

            frm.clear_table("table_hrug");

            r.message.forEach(d => {

                let row = frm.add_child("table_hrug");

                row.interest_date = d.interest_date;
                row.opening_face_value = d.opening_face_value;
                row.interest_amount = d.interest_amount;
                row.closing_value = d.closing_value;
                row.days = d.days;

            });

            frm.refresh_field("table_hrug");

        }
    });
}