// Copyright (c) 2026, CSM Technologies Pvt Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on("Stop Increment Panel", {
    onload(frm){
        frm.add_custom_button("Mark Stop Increment", () => {
            mark_stop_increment(frm);
        });
    },
    refresh(frm) {
        frm.disable_save();
        
        if (!frm.datatable) {
            frm.trigger("get_employees");
        }
        
        frm.add_custom_button("Apply Stop Increment", () => {
            apply_stop_increment(frm);
        });
        frm.add_custom_button("Mark Stop Increment", () => {
            mark_stop_increment(frm);
        });
        frm.add_custom_button("Export Report", () => {
            export_increment(frm);
        });
        frm.add_custom_button("Set Reason", () => {
            set_reason(frm);
        });
    },
    company(frm){
        frm.trigger("get_employees");
    },
    increment_month(frm){
        frm.trigger("get_employees");
    },
    get_employees(frm) {

        if (!frm.doc.company || !frm.doc.increment_month || !frm.doc.effective_date) {
            return;
        }

        frappe.call({
            method: "nafed_erp.hire_to_retire.doctype.stop_increment_panel.stop_increment_panel.get_employees",
            args: {
                company: frm.doc.company,
                increment_month: frm.doc.increment_month,
                effective_date: frm.doc.effective_date
            }
        }).then(r => {

            let columns = frm.events.get_columns();
            frm.events.render_datatable(frm, columns, r.message || []);

        });
    },

    // ----------------------------
    // DATATABLE COLUMNS
    // ----------------------------
    get_columns() {
        return [
            { name: "Employee", id: "employee", editable: false },
            { name: "Name", id: "employee_name", editable: false },
            { name: "Stop?", id: "stop_increment", editable: false },
            { name: "Reason", id: "reason", editable: false }
        ];
    },

    // ----------------------------
    // RENDER DATATABLE
    // ----------------------------
    render_datatable(frm, columns, data) {

        let wrapper = frm.fields_dict.employees_table.$wrapper;
        wrapper.empty();
    
        // 🔥 convert object → array (stable format)
        let table_data = (data || []).map(d => [
            d.employee,
            d.employee_name,
            d.stop_increment || 0,
            d.reason || ""
        ]);
    
        // ✅ source of truth
        frm._table_data = table_data;
    
        frm.datatable = new frappe.DataTable(wrapper[0], {
            columns: columns,
            data: table_data,
            checkboxColumn: true,
            layout: "fluid",
    
            // 🔥 THIS IS THE KEY FIX
            events: {
                onCellEdit: (cell) => {
    
                    let r = cell.rowIndex;
                    let c = cell.colIndex;
                    let value = cell.value;
    
                    // force value
                    value = value || "";
    
                    // ✅ update source
                    frm._table_data[r][c] = value;
    
                    console.log("UPDATED ROW:", frm._table_data[r]);
                }
            }
        });
    },
    effective_date(frm) {
        
        let today = frappe.datetime.get_today();
        let effective_date = frm.doc.effective_date;

        // ----------------------------
        // ❌ Past Date Validation
        // ----------------------------
        if (effective_date < today) {

            frappe.msgprint("Effective Date cannot be less than today");

            frm.__updating_effective_date = true;

            frm.set_value("effective_date", today).then(() => {
                frm.__updating_effective_date = false;
            });

            return;
        }
    }
});


function apply_stop_increment(frm) {

    if (!frm.datatable) {
        frappe.msgprint("No data available");
        return;
    }

    let selected = [];
    let invalid_rows = [];

    frm.datatable.rowmanager.checkMap.forEach((checked, idx) => {
        if (checked) {

            let row = frm._table_data[idx];

            let stop = row[2];   // stop_increment
            let reason = row[3]; // reason

            // 🔥 ONLY PROCESS stop_increment = 1
            if (stop == 1) {

                // ❌ validation
                if (!reason || reason.trim() === "") {
                    invalid_rows.push(row[0]); // employee code
                }

                selected.push({
                    employee: row[0],
                    employee_name: row[1],
                    stop_increment: stop,
                    reason: reason
                });
            }
        }
    });

    // ❌ no valid rows to process
    if (!selected.length) {
        frappe.msgprint("No employees marked for Stop Increment");
        return;
    }

    // 🚨 BLOCK IF INVALID
    if (invalid_rows.length) {
        frappe.msgprint({
            title: "Validation Error",
            indicator: "red",
            message: `
                Reason is mandatory to Stop Increment.<br><br>
                Missing for employees:<br>
                <b>${invalid_rows.join(", ")}</b>
            `
        });
        return;
    }

    // ✅ proceed
    frappe.confirm(
        `Stop increment for ${selected.length} employee(s)?`,
        () => {

            frappe.call({
                method: "nafed_erp.hire_to_retire.doctype.stop_increment_panel.stop_increment_panel.apply_stop_increment",
                args: {
                    employees: selected,
                    effective_date: frm.doc.effective_date,
                    increment_month: frm.doc.increment_month
                },
                freeze: true,
                freeze_message: "Applying Stop Increment..."
            }).then(() => {

                frappe.msgprint("Stop Increment Applied Successfully");

                frm.datatable = null;
                frm.trigger("get_employees");
            });
        }
    );
}

function mark_stop_increment(frm) {

    if (!frm.datatable) {
        frappe.msgprint("No data available");
        return;
    }

    let selected = [];

    frm.datatable.rowmanager.checkMap.forEach((checked, idx) => {
        if (checked) selected.push(idx);
    });

    if (!selected.length) {
        frappe.msgprint("Please select employees");
        return;
    }

    selected.forEach(idx => {
        frm._table_data[idx][2] = 1;  // stop_increment column
    });

    // 🔥 DO FULL REFRESH (NOT refreshRow)
    frm.datatable.refresh(frm._table_data);

    frappe.msgprint(`${selected.length} employee(s) marked for Stop Increment`);
}


function export_increment(frm) {

    let selected = [];

    frm.datatable.rowmanager.checkMap.forEach((checked, idx) => {
        if (checked) {

            let row = frm._table_data[idx];

            selected.push({
                employee: row[0],
                employee_name: row[1],
                stop_increment: row[2],
                reason: row[3]
            });
        }
    });

    if (!selected.length) {
        frappe.msgprint("Please select employees");
        return;
    }

    frappe.call({
        method: "nafed_erp.hire_to_retire.doctype.stop_increment_panel.stop_increment_panel.export_stop_increment_report",
        args: {
            employees: selected,
            increment_month: frm.doc.increment_month,
            effective_date: frm.doc.effective_date
        }
    }).then(r => {
        if (r.message) window.open(r.message);
    });
}

function set_reason(frm) {

    if (!frm.datatable) {
        frappe.msgprint("No data available");
        return;
    }

    let selected = [];

    frm.datatable.rowmanager.checkMap.forEach((checked, idx) => {
        if (checked) selected.push(idx);
    });

    if (!selected.length) {
        frappe.msgprint("Please select employees");
        return;
    }

    let d = new frappe.ui.Dialog({
        title: "Set Reason",
        fields: [
            {
                label: "Reason",
                fieldname: "reason",
                fieldtype: "Small Text",
                reqd: 1
            }
        ],
        primary_action_label: "Update",
        primary_action(values) {

            let reason = values.reason;

            selected.forEach(idx => {

                // 🔥 EXACT SAME PATTERN AS YOUR WORKING CODE
                frm._table_data[idx][3] = reason;  // reason column
            });

            // 🔥 IMPORTANT: full refresh (not refreshRow)
            frm.datatable.refresh(frm._table_data);

            d.hide();

            frappe.msgprint(`${selected.length} employee(s) updated with reason`);
        }
    });

    d.show();
}