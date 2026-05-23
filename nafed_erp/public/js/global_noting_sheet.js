// console.log("NOTING SHEET: FINAL MERGED VERSION");

// CLOSED STATES
const CLOSED_STATES = ["closed", "completed", "approved", "rejected"];


// 🔥 GLOBAL TRIGGER (ONLY CHANGE)
frappe.router.on('change', () => {
    setTimeout(() => {
        if (cur_frm) {
            apply_noting_logic(cur_frm);
        }
    }, 500);
});



function apply_noting_logic(frm) {

    if (frm.doctype === "DocType" || !frm.get_field('logs')) return;

    // console.log("NOTING SHEET: Applying on ->", frm.doctype);

    let workflow_state = (frm.doc.workflow_state || "").toLowerCase();
    let is_closed = CLOSED_STATES.includes(workflow_state);

    if (!is_closed) {

        frm.remove_custom_button(__('Add Noting'));

        setTimeout(() => {
            frm.add_custom_button(__('Add Noting'), function () {
                open_noting_remark_dialog(frm);
            });
            // console.log("Button Added ✅ for", frm.doctype);
        }, 200);
    }

    apply_global_row_permissions(frm);
}


// CHILD TABLE EVENTS (UNCHANGED)
frappe.ui.form.on("Complaint Receipts Remarks", {
    form_render(frm) {
        apply_global_row_permissions(frm);
    },
    logs_add(frm) {
        apply_global_row_permissions(frm);
    }
});


// REMARK POPUP (UNCHANGED)
function open_noting_remark_dialog(frm) {

    frappe.prompt([
        {
            fieldname: "remark_text",
            fieldtype: "Text Editor",
            label: "Add Noting",
            reqd: 1
        }
    ],
    function(values) {

        let plain_text = $("<div>").html(values.remark_text).text().trim();

        if (!plain_text) {
            frappe.show_alert({
                message: __("Noting cannot be empty."),
                indicator: "red"
            });
            return;
        }

        let row = frm.add_child("logs");
        row.action_taken_by = frappe.session.user;
        row.action_taken_on = frappe.datetime.get_today();
        row.remarks = values.remark_text;

        frm.refresh_field("logs");
        frm.save();
    },
    __("Noting"),
    __("Submit"));
}


// ROW PERMISSION (UNCHANGED)
function apply_global_row_permissions(frm) {

    if (!frm.doc.logs || !frm.get_field('logs')) return;

    let workflow_state = (frm.doc.workflow_state || "").toLowerCase();
    let is_closed = CLOSED_STATES.includes(workflow_state);

    if (frm.fields_dict.logs && frm.fields_dict.logs.grid) {

        frm.fields_dict.logs.grid.grid_rows.forEach(function(row) {

            // let is_admin = frappe.session.user === "Administrator";
            let is_creator = row.doc.action_taken_by === frappe.session.user;

            if (is_closed) {
                row.toggle_editable("remarks", false);
            } else {
                row.toggle_editable("remarks", is_creator);
            }

            row.toggle_editable("action_taken_by", false);
            row.toggle_editable("action_taken_on", false);
        });
    }
}