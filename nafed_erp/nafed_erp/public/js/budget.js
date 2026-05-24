frappe.ui.form.on('Budget', {
    refresh: function(frm) {

        let field = frm.get_field("budget_against");
        let options = field.df.options.split("\n");
        let cleaned_options = options.filter(opt => opt.trim() !== "");
        frm.set_df_property("budget_against", "options", cleaned_options.join("\n"));
        frm.refresh_field("budget_against");
    }
});
