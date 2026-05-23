frappe.ui.form.on('Payment Entry', {
    paid_amount: function(frm) {
        auto_set_payment_mode(frm);
    },
    party: function(frm) {
        auto_set_payment_mode(frm);
    }
});

function auto_set_payment_mode(frm) {
    const amount = frm.doc.paid_amount;

    if (!amount) return;

    frappe.call({
        method: "nafed_erp.finance_and_accounts.doctype.payment_mode_rules_settings.payment_mode_rules_settings.get_payment_mode",
        args: {
            amount: amount,
            party_type: frm.doc.party_type
        },
        callback: function(r) {
            if (!r.message) {
                frappe.msgprint(`No payment rule found for amount: ${amount} in Payment Mode Rules Settings`);
                return;
            }

            const rule = r.message;

            // Delay to avoid ERPNext resetting the field
            setTimeout(() => {
                frm.set_value("mode_of_payment", rule.mode_of_payment);

                frappe.show_alert({
                    message: `Mode of Payment automatically set to <b>${rule.mode_of_payment}</b>`,
                    indicator: 'green'
                });
            }, 300);
        }
    });
}

frappe.ui.form.on("Payment Entry", {
    refresh(frm) {
        toggle_pf_fields(frm);
    },

    company(frm) {
        toggle_pf_fields(frm);
    }
});

function toggle_pf_fields(frm) {
    if (!frm.doc.company) return;

    frappe.db.get_value("Company", frm.doc.company, "custom_is_pf_trust")
        .then(r => {
            let is_pf_trust = r.message.custom_is_pf_trust;

            frm.toggle_display("custom_face_value", is_pf_trust);
            frm.toggle_display("custom_pf_investment", is_pf_trust);
            frm.toggle_display("custom_interest_paid", is_pf_trust);
            frm.toggle_display("custom_total_amount", is_pf_trust);
        });
}


frappe.ui.form.on("Payment Entry", {

    refresh(frm) {
        apply_party_filter(frm);
    },

    custom_payment_transfer(frm) {
        frm.set_value("party", "");
        frm.set_value("party_type", "Supplier");
        apply_party_filter(frm);
    },

    party_type(frm) {
        apply_party_filter(frm);
    }

});

function apply_party_filter(frm) {

    frm.set_query("party", function() {

        let filters = {};

        if (frm.doc.custom_payment_transfer === "Payment To Farmer") {
            filters["custom_is_farmer"] = 1;
        }

        if (frm.doc.custom_payment_transfer === "Payment To Society") {
            filters["custom_is_sla"] = 1;
        }

        if (frm.doc.custom_payment_transfer === "Payment To Other Vendor") {
            filters["custom_other"] = 1;
        }

        return {
            filters: filters
        };

    });

}


frappe.ui.form.on("Payment Entry", {

    custom_cheque_book_: function(frm) {

        if (!frm.doc.custom_cheque_book_) {
            frm.set_value("custom_list_of_cheque_book", "");
            return;
        }

        frappe.db.get_doc("Cheque Book", frm.doc.custom_cheque_book_)
            .then(doc => {

                let cheque_list = [];

                if (doc.cheque_leaves && doc.cheque_leaves.length > 0) {

                    doc.cheque_leaves.forEach(row => {

                        // ✅ Only show AVAILABLE cheques
                        if (row.cheque_no && row.status === "Available") {
                            cheque_list.push(row.cheque_no);
                        }
                    });
                }

                frm.set_df_property(
                    "custom_list_of_cheque_book",
                    "options",
                    cheque_list.join("\n")
                );

                frm.refresh_field("custom_list_of_cheque_book");
            });
    },

    custom_list_of_cheque_book: function(frm) {
        if (frm.doc.custom_list_of_cheque_book) {
            frm.set_value("reference_no", frm.doc.custom_list_of_cheque_book);
        }
    }
});


frappe.ui.form.on("Payment Entry", {
    on_submit: function(frm) {

        if (!frm.doc.custom_cheque_book_ || !frm.doc.reference_no) {
            return;
        }

        frappe.call({
            method: "frappe.client.get",
            args: {
                doctype: "Cheque Book",
                name: frm.doc.custom_cheque_book_
            },
            callback: function(res) {

                let cheque_book = res.message;

                let used_count = 0;
                let total_count = cheque_book.cheque_leaves.length;

                // ✅ Update cheque row
                cheque_book.cheque_leaves.forEach(row => {

                    if (String(row.cheque_no).trim() === String(frm.doc.reference_no).trim()) {

                        row.status = "Issued";
                        row.voucher_type = "Payment Entry";
                        row.voucher_no = frm.doc.name;
                        row.amount = frm.doc.paid_amount;
                        row.party_type = frm.doc.party_type;
                        row.party = frm.doc.party;
                        row.issue_date = frm.doc.posting_date;
                    }

                    // ✅ Count issued cheques
                    if (row.status === "Issued") {
                        used_count++;
                    }
                });

                let pending_count = total_count - used_count;

                // ✅ Decide Cheque Book Status
                let cheque_book_status = "Unused";

                if (used_count > 0 && used_count < total_count) {
                    cheque_book_status = "Used";
                }

                if (used_count === total_count) {
                    cheque_book_status = "Closed";
                }

                // ✅ Set counts in parent (make sure fields exist)
                cheque_book.used_cheques = used_count;
                cheque_book.pending_cheques = pending_count;
                cheque_book.status = cheque_book_status;

                // ✅ Save
                frappe.call({
                    method: "frappe.client.save",
                    args: {
                        doc: cheque_book
                    },
                    callback: function() {
                        frappe.msgprint("✅ Cheque Book Updated Successfully");
                    }
                });
            }
        });
    }
});