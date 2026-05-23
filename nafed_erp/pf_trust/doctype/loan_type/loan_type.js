frappe.ui.form.on("Loan Type", {
    refresh: function(frm) {
        hide_add_row_after_render(frm);
    }
});

// Child table events
frappe.ui.form.on("Housing Rule", {

    housing_rules_add: function(frm) {
        hide_add_row_after_render(frm);
    },

    housing_rules_remove: function(frm) {
        hide_add_row_after_render(frm);
    },

    sub_category(frm, cdt, cdn) {
        hide_add_row_after_render(frm);
    }
});

function hide_add_row_after_render(frm) {
    const max_rows = 1;

    // wait for grid re-render
    setTimeout(() => {
        const row_count = frm.doc.housing_rules
            ? frm.doc.housing_rules.length
            : 0;

        const grid = frm.fields_dict.housing_rules.grid;

        if (row_count >= max_rows) {
            grid.wrapper.find(".grid-add-row").hide();
        } else {
            grid.wrapper.find(".grid-add-row").show();
        }
    }, 100);
}