// ==============================
// SEED PURCHASE
// ==============================

frappe.ui.form.on('Seed Purchase', {

    refresh: function(frm) {

        if (!frm.is_new()) {
            frm.add_custom_button('Create Payment', function() {
                create_payment(frm);
            }, 'Create');
        }

        fetch_rates(frm);
        calculate_totals(frm);
    },

    validate: function(frm) {
        calculate_totals(frm);
    }

});
frappe.ui.form.on('Seed Purchase', {

    refresh: function(frm) {

        // 🔥 Only after submit
        if (frm.doc.docstatus === 1) {

            frm.add_custom_button('Create Seed Issue', function() {
                create_seed_issue(frm);
            }, 'Create');

        }
    }
});
function create_seed_issue(frm) {

    frappe.model.with_doctype('Seed Issue', function() {

        let doc = frappe.model.get_new_doc('Seed Issue');

        doc.supplier = frm.doc.supplier;
        doc.seed_purchase = frm.doc.name;
        doc.issue_date = frappe.datetime.nowdate();
        doc.status = "Draft";

        // 🔥 VERY IMPORTANT FIELDNAME
        (frm.doc.seed_purchase_item || []).forEach(function(item) {

            let row = frappe.model.add_child(
                doc,
                'Seed Issue Item',     // child doctype name
                'seed_issue_items'               // 🔥 MUST match fieldname in parent doctype
            );

            row.crop = item.crop;
            row.variety = item.variety;
            row.quantity = item.quantity;
            row.rate = item.rate;
            row.amount = item.amount;
        });

        frappe.set_route('Form', 'Seed Issue', doc.name);
    });
}
// ==============================
// FETCH RATE FROM PRICE MASTER
// ==============================

function fetch_rates(frm) {

    (frm.doc.seed_purchase_item || []).forEach(function(row) {

        if (!row.crop || !row.variety || !frm.doc.supplier) return;

        frappe.db.get_value('Seed Price', {
            crop: row.crop,
            variety: row.variety,
            supplier: frm.doc.supplier
        }, 'rate', function(r) {

            if (r && r.rate) {

                row.rate = r.rate;
                row.amount = row.rate * (row.quantity || 0);

                frm.refresh_field('seed_purchase_item');
                calculate_totals(frm);
            }
        });

    });
}

// ==============================
// CALCULATE TOTALS
// ==============================

function calculate_totals(frm) {

    let total_qty = 0;
    let total_amount = 0;

    (frm.doc.seed_purchase_item || []).forEach(function(d) {

        d.amount = (d.quantity || 0) * (d.rate || 0);

        total_qty += d.quantity || 0;
        total_amount += d.amount || 0;
    });

    frm.set_value("total_quantity", total_qty);
    frm.set_value("total_amount", total_amount);

    frm.refresh_field("seed_purchase_item");
}

// ==============================
// CREATE SUPPLIER PAYMENT
// ==============================

function create_payment(frm) {

    if (!frm.doc.total_amount || frm.doc.total_amount === 0) {
        frappe.msgprint("Total Amount is missing in Seed Purchase");
        return;
    }

    frappe.model.with_doctype('Supplier Payment', function() {

        let doc = frappe.model.get_new_doc('Supplier Payment');

        doc.supplier = frm.doc.supplier;
        doc.seed_purchase = frm.doc.name;
        doc.payment_date = frappe.datetime.nowdate();

        doc.total_payable = frm.doc.total_amount;
        doc.amount_paid = 0;
        doc.balance_amount = frm.doc.total_amount;

        doc.status = "Pending";

        frappe.set_route('Form', 'Supplier Payment', doc.name);
    });
}

// ==============================
// SUPPLIER PAYMENT
// ==============================

frappe.ui.form.on('Supplier Payment', {

    // 🔹 Fetch total when selecting Seed Purchase
    seed_purchase: function(frm) {

        if (!frm.doc.seed_purchase) return;

        frappe.db.get_value(
            'Seed Purchase',
            frm.doc.seed_purchase,
            'total_amount',
            function(r) {

                if (r && r.total_amount) {

                    frm.set_value('total_payable', r.total_amount);
                    frm.set_value('balance_amount', r.total_amount);
                }
            }
        );
    },

    // 🔹 Calculate balance when paid changes
    amount_paid: function(frm) {

        let total = frm.doc.total_payable || 0;
        let paid = frm.doc.amount_paid || 0;

        if (paid > total) {
            frappe.msgprint("Paid amount cannot exceed total");
            frm.set_value('amount_paid', total);
            paid = total;
        }

        frm.set_value('balance_amount', total - paid);
    }
});