// Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on("Fumigation Schedule", {

    refresh(frm) {

        // Show button only after submit
        if (frm.doc.docstatus === 1) {

            frm.add_custom_button(
                __("Treatment Execution"),

                function () {

                    frappe.new_doc(
                        "Treatment Execution",

                        {
                            schedule_reference: frm.doc.name,
                            warehouse: frm.doc.warehouse,
                            treatment_type: frm.doc.treatment_type,
                            scheduled_date: frm.doc.scheduled_date
                        }
                    );

                }
            );
        }
    }
});
