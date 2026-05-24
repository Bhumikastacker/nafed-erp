frappe.ready(() => {

    const params = new URLSearchParams(window.location.search);
    const rfq = params.get("rfq");
    const supplier = params.get("supplier");

    if (!rfq) return;

    frappe.call({
        method: "nafed_erp.procure_to_pay.doc_events.request_for_quotation.get_rfq_data",
        args: {
            rfq: rfq,
            supplier: supplier
        },
        callback: function(r) {

            let data = r.message;

            setTimeout(() => {

                frappe.web_form.set_value("quotation_number", rfq);

                setTimeout(() => {
                    frappe.web_form.set_value("company", data.company_name);
                }, 200);

                setTimeout(() => {
                    if (supplier) {
                        frappe.web_form.set_value("supplier", supplier);
                    }
                }, 400);

                setTimeout(() => {
                    frappe.web_form.set_value("supplier_name", data.supplier_name);
                }, 600);

                let grid = frappe.web_form.fields_dict.items.grid;

                // Clear table
                grid.df.data = [];
                grid.refresh();

                // Add rows
                data.items.forEach(item => {
                    grid.add_new_row();

                    let row = grid.df.data[grid.df.data.length - 1];
                    if (!row) return;

                    row.item_code = item.item_code;
                    row.item_name = item.item_name;
                    row.description = item.description;
                    row.qty = item.qty;
                    row.uom = item.uom;
                    row.rate = 0;
                });

                grid.refresh();

                // Disable add/delete
                grid.cannot_add_rows = true;
                grid.cannot_delete_rows = true;
                grid.refresh();

                // 🔥 HARD LOCK USING DOM
                setTimeout(() => {

                    // Disable all inputs except rate
                    document.querySelectorAll('.grid-row').forEach(row => {

                        row.querySelectorAll('input, select, textarea').forEach(input => {

                            let fieldname = input.getAttribute("data-fieldname");

                            if (fieldname !== "rate") {
                                input.setAttribute("readonly", true);
                                input.setAttribute("disabled", true);
                                input.style.pointerEvents = "none";
                                input.style.backgroundColor = "#f5f5f5";
                            } else {
                                input.removeAttribute("readonly");
                                input.removeAttribute("disabled");
                                input.style.pointerEvents = "auto";
                                input.style.backgroundColor = "";
                            }

                        });

                    });

                }, 300);

            }, 800);

        }
    });

});




function lock_grid_fields() {
    let rows = document.querySelectorAll('.grid-row');

    rows.forEach(row => {

        row.querySelectorAll('[data-fieldname]').forEach(el => {

            let fieldname = el.getAttribute("data-fieldname");

            // 🔥 Hide amount field completely
            if (fieldname === "amount") {
                let field_area = el.closest('.form-group, .grid-static-col, .grid-input-col');
                if (field_area) {
                    field_area.style.display = "none";
                } else {
                    el.style.display = "none";
                }
                return;
            }

            // 🔒 Lock all except rate
            if (["input", "select", "textarea"].includes(el.tagName.toLowerCase())) {

                if (fieldname !== "rate") {
                    el.setAttribute("readonly", true);
                    el.setAttribute("disabled", true);
                    el.style.pointerEvents = "none";
                    el.style.backgroundColor = "#f5f5f5";
                } else {
                    el.removeAttribute("readonly");
                    el.removeAttribute("disabled");
                    el.style.pointerEvents = "auto";
                    el.style.backgroundColor = "";
                }

            }

        });

    });
}
// 🔥 Run multiple times (handles re-render)
setTimeout(lock_grid_fields, 300);
setTimeout(lock_grid_fields, 800);
setTimeout(lock_grid_fields, 1500);

// 🔥 Mutation Observer (ultimate fix)
const observer = new MutationObserver(() => {
    lock_grid_fields();
});

observer.observe(document.body, {
    childList: true,
    subtree: true
});






