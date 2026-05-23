frappe.after_ajax(() => {

    if (frappe._global_save_patch) return;
    frappe._global_save_patch = true;

    const original_frappe_save = frappe.ui.form.save;

    frappe.ui.form.save = function (frm, action, callback, btn) {

        // Intercept ONLY Save
        if (action === "Save" && !frm.__confirming_save) {

            frappe.confirm(
                __("Do you really want to save this document?"),
                () => {
                    // YES → proceed
                    frm.__confirming_save = true;
                    frappe.ui.form.save(frm, action, callback, btn);
                    frm.__confirming_save = false;
                },
                () => {
                    // NO → fix disabled button
                    if (btn) {
                        $(btn).prop("disabled", false);
                        $(btn).removeClass("disabled");
                    }

                    frappe.show_alert({
                        message: __("Save Cancelled"),
                        indicator: "red"
                    });
                }
            );

            return;   // stop original save
        }

        // Continue with default save for Submit/Cancel actions
        return original_frappe_save(frm, action, callback, btn);
    };
});