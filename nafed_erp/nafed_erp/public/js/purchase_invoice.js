
frappe.ui.form.on("Purchase Invoice", {

    /* -------------------------------------------------- */
    /* SUPPLIER CHANGE */
    /* -------------------------------------------------- */
    supplier(frm) {

        // Reset everything
        frm.clear_table("custom_case_and_hearing_details");
        // frm.clear_table("items");
        frm.refresh_fields(["custom_case_and_hearing_details", "items"]);

        // Hide by default
        frm.toggle_display("custom_case_and_hearing_details", false);
        frm.toggle_display("custom_case_id", false);

        // Reset temp vars
        frm._legal_advocate = null;
        frm._fee_schedule = null;
        frm._advocate_rate = 0;

        if (!frm.doc.supplier) return;

        // Check Supplier Group
        frappe.db.get_value("Supplier", frm.doc.supplier, "supplier_group")
            .then(r => {

                if (r.message?.supplier_group === "Advocate") {

                    // Show empty table + case field
                    frm.toggle_display("custom_case_and_hearing_details", true);
                    frm.toggle_display("custom_case_id", true);

                    fetch_legal_advocate(frm);
                }
            });
    },

    /* -------------------------------------------------- */
    /* CASE ID SELECTED */
    /* -------------------------------------------------- */
    custom_case_id(frm) {

        frm.clear_table("custom_case_and_hearing_details");
        frm.clear_table("items");
        frm.refresh_fields(["custom_case_and_hearing_details", "items"]);

        if (!frm.doc.custom_case_id) return;

        fetch_cases_and_hearings(frm);
    },

    /* -------------------------------------------------- */
    /* ON SUBMIT → LINK HEARINGS */
    /* -------------------------------------------------- */
    on_submit(frm) {

        (frm.doc.custom_case_and_hearing_details || []).forEach(row => {
            if (row.hearing_id) {
                frappe.db.set_value(
                    "Legal Case Hearing",
                    row.hearing_id,
                    "purchase_invoice",
                    frm.doc.name
                );
            }
        });
    }
});


/* ================================================== */
/* FETCH LEGAL ADVOCATE */
/* ================================================== */
function fetch_legal_advocate(frm) {

    frappe.call({
        method: "frappe.client.get_list",
        args: {
            doctype: "Legal Advocates",
            filters: {
                is_supplier: 1,
                name1: frm.doc.supplier
            },
            fields: ["name", "advocate_fee_schedule"],
            limit_page_length: 1
        },
        callback(r) {

            if (!r.message || !r.message.length) {
                frappe.msgprint({
                    title: "Legal Advocate Missing",
                    message: "No Legal Advocate found for this Supplier",
                    indicator: "red"
                });
                return;
            }

            frm._legal_advocate = r.message[0].name;
            frm._fee_schedule = r.message[0].advocate_fee_schedule;

            if (!frm._fee_schedule) {
                frappe.throw("Advocate Fee Schedule not linked in Legal Advocates");
            }

            // ✅ SET ADVOCATE-WISE CASE FILTER
            set_case_query(frm);

            fetch_advocate_fee(frm);
        }
    });
}


/* ================================================== */
/* SET CASE QUERY (ADVOCATE WISE FILTER) */
/* ================================================== */
function set_case_query(frm) {

    frm.set_query("custom_case_id", function () {
        return {
            filters: {
                assigned_advocate: frm._legal_advocate,
                status: ["in", [
                "Registered",
                "Closed"
    ]]
            }
        };
    });
}


/* ================================================== */
/* FETCH ADVOCATE FEE */
/* ================================================== */
function fetch_advocate_fee(frm) {

    frappe.call({
        method: "frappe.client.get_value",
        args: {
            doctype: "Advocate Fee Schedule",
            filters: { name: frm._fee_schedule },
            fieldname: "rate"
        },
        callback(r) {
            frm._advocate_rate = flt(r.message?.rate || 0);
            // ❌ NO AUTO LOADING OF CASES HERE
        }
    });
}


/* ================================================== */
/* FETCH CASES & HEARINGS (ONLY SELECTED CASE) */
/* ================================================== */
async function fetch_cases_and_hearings(frm) {

    frm.clear_table("custom_case_and_hearing_details");

    if (!frm._legal_advocate) return;

    let cases = await frappe.db.get_list("Legal Case Registration", {
        filters: {
            name: frm.doc.custom_case_id,
            assigned_advocate: frm._legal_advocate,
             status: ["in", [
                   "Registered",
                 "Closed"
    ]]
        },
            fields: ["name", "case_category", "status"]   
 });

    if (!cases.length) {
        frappe.msgprint({
            title: "Invalid Case",
            message: "Selected Case does not belong to this Advocate",
            indicator: "orange"
        });
        return;
    }

    let total_hearings = 0;

    for (let c of cases) {

        let hearings = await frappe.db.get_list("Legal Case Hearing", {
            filters: {
                case_id: c.name,
                advocate: frm._legal_advocate,
                purchase_invoice: ["is", "not set"]
            },
            fields: ["name"]
        });

        for (let h of hearings) {

            let row = frm.add_child("custom_case_and_hearing_details");
            row.case_id = c.name;
            row.case_category = c.case_category;
            row.hearing_id = h.name;
            row.status = c.status;
            total_hearings++;
        }
    }

    if (total_hearings === 0) {

        frm.clear_table("custom_case_and_hearing_details");
        frm.clear_table("items");
        frm.refresh_fields(["custom_case_and_hearing_details", "items"]);

        frappe.msgprint({
            title: "Nothing to Invoice",
            message: "No pending hearings for this Case",
            indicator: "green"
        });

        return;
    }

    frm.refresh_field("custom_case_and_hearing_details");

    let total_amount = frm._advocate_rate * total_hearings;
    set_invoice_item(frm, total_amount);
}


/* ================================================== */
/* SET PURCHASE INVOICE ITEM */
/* ================================================== */
function set_invoice_item(frm, amount) {

    frm.clear_table("items");

    if (!amount || amount <= 0) {
        frm.refresh_field("items");
        return;
    }

    let item = frm.add_child("items");
    item.item_code = "Service Item"; // MUST EXIST
    item.item_name = item.item_code;
    item.qty = 1;
    item.rate = amount;
    item.amount = amount;
    item.net_rate = amount;
    item.net_amount = amount;
    item.uom = "Nos";

    frm.refresh_field("items");
    frm.trigger("calculate_taxes_and_totals");
}

frappe.ui.form.on("Purchase Invoice", {

    supplier: function(frm) {

        if (!frm.doc.supplier) return;

        frappe.db.get_doc("Supplier", frm.doc.supplier).then(supplier => {

            if (supplier.supplier_group != "Statutory") return;
            if (!supplier.custom_auditor_empanelment) return;

            // CHECK if invoice already exists
            frappe.call({
                method: "frappe.client.get_list",
                args: {
                    doctype: "Purchase Invoice",
                    filters: {
                        supplier: frm.doc.supplier,
                        docstatus: ["!=", 2]
                    },
                    fields: ["name"],
                    limit_page_length: 1
                },
                callback: function(r) {

                    if (r.message && r.message.length > 0) {

                        frappe.msgprint({
                            title: "Warning",
                            message: "Invoicing already done. Kindly check the transactions.",
                            indicator: "red"
                        });

                        // Clear items and stop
                        frm.clear_table("items");
                        frm.refresh_field("items");
                        return;
                    }

                    // IF NOT EXIST → FETCH AUDITOR EMPANELMENT
                    frappe.db.get_doc("Auditor Empanelment", supplier.custom_auditor_empanelment)
                    .then(auditor => {

                        frm.clear_table("items");

                        // Parent rate
                        if (auditor.rate) {

                            let row = frm.add_child("items");
                            row.item_code = "Service Item";
                            row.item_name = "Service Item";
                            row.qty = 1;
                            row.uom = "Nos";
                            row.stock_uom = "Nos";
                            row.rate = auditor.rate;
                            row.custom_ref = supplier.custom_auditor_empanelment;

                        }

                        // Child table rates
                        if (auditor.add_others_auditor_empanelment) {

                            auditor.add_others_auditor_empanelment.forEach(d => {

                                if (d.rate) {

                                    let child = frm.add_child("items");
                                    child.item_code = "Service Item";
                                    child.item_name = "Service Item";
                                    child.qty = 1;
                                    child.uom = "Nos";
                                    child.stock_uom = "Nos";
                                    child.rate = d.rate;
                                    child.custom_ref = supplier.custom_auditor_empanelment;

                                }

                            });

                        }

                        frm.refresh_field("items");

                    });

                }
            });

        });

    },


    on_submit: function(frm) {

        if (!frm.doc.supplier) return;

        frappe.call({
            method: "nafed_erp.finance_and_accounts.doctype.auditor_empanelment.auditor_empanelment.update_auditor_empanelment",
            args: {
                purchase_invoice: frm.doc.name,
                supplier: frm.doc.supplier
            }
        });

    }

});