frappe.ui.form.on("Increment Control Panel", {
    onload(frm) {
        frm.add_custom_button("Apply Increment", () => {
            apply_increment(frm);
        });
        frm.add_custom_button("Set Next Basic", () => {
            set_next_basic(frm);
        });
    },
	refresh(frm) {
		frm.disable_save();
		if (!frm.datatable) {
            frm.trigger("get_employees");
        }
        frm.add_custom_button("Export Report", () => {
            export_increment(frm);
        });
        frm.add_custom_button("Apply Increment", () => {
            apply_increment(frm);
        });
        frm.add_custom_button("Set Next Basic", () => {
            set_next_basic(frm);
        });
	},
    company(frm){
        frm.trigger("get_employees");
    },
    increment_month(frm){
        frm.trigger("get_employees");
    },
    effective_date(frm) {

        if (frm.doc.effective_date) {
    
            let today = frappe.datetime.get_today();
    
            if (frm.doc.effective_date < today) {
    
                frappe.msgprint("Effective Date cannot be less than today");
    
                // 🔥 reset to today
                frm.set_value("effective_date", today);
            }
        }
    },
	// ----------------------------
	// FETCH EMPLOYEES
	// ----------------------------
	get_employees(frm) {
        if (!frm.doc.company || !frm.doc.effective_date) return;
    
    
        frappe.call({
            method: "nafed_erp.hire_to_retire.doctype.increment_control_panel.increment_control_panel.get_employees",
            args: {
                company: frm.doc.company,
                effective_date: frm.doc.effective_date,
                increment_month: frm.doc.increment_month
            }
        }).then(r => {
    
            console.log("DATA:", r.message);
    
            const columns = frm.events.get_columns();
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
            { name: "Current Basic", id: "current_basic", editable: false },
            { name: "Last Increment", id: "last_increment", editable: false },
            { name: "New Basic", id: "new_basic", editable: false }
        ];
    },

	// ----------------------------
	// RENDER DATATABLE
	// ----------------------------
	render_datatable(frm, columns, data) {

        let wrapper = frm.fields_dict.employees_table.$wrapper;
    
        wrapper.empty();
        wrapper.css("min-height", "400px");
    
        (data || []).forEach(row => {
            row.current_basic = flt(row.current_basic);
            row.new_basic = flt(row.current_basic);
            row.basic_pay_options = (row.basic_pay_options || []).map(v => flt(v));
        });
    
        frm.datatable = new frappe.DataTable(wrapper[0], {
            columns: columns,
            data: data,
            checkboxColumn: true,
            inlineFilters: true,
            layout: "fluid",
        
            // 🔥 THIS LINE FIXES EVERYTHING
            serialNoColumn: false
        });
    }
});
function apply_increment(frm) {

    if (!frm.datatable) {
        frappe.msgprint("No data available");
        return;
    }

    let selected = [];
    let invalid_rows = [];

    let check_map = frm.datatable.rowmanager.checkMap;

    check_map.forEach((checked, idx) => {
        if (checked) {

            let row = frm.datatable.datamanager.data[idx];

            let current_basic = flt(row.current_basic || 0);
            let new_basic = flt(row.new_basic || 0);

            // ❌ validation
            if (current_basic === new_basic) {
                invalid_rows.push(row.employee);
            }

            selected.push(row);
        }
    });

    if (!selected.length) {
        frappe.msgprint("Please select employees");
        return;
    }

    // 🚨 BLOCK IF INVALID
    if (invalid_rows.length) {
        frappe.msgprint({
            title: "Validation Error",
            indicator: "red",
            message: `
                New Basic cannot be same as Current Basic.<br><br>
                Invalid for employees:<br>
                <b>${invalid_rows.join(", ")}</b>
            `
        });
        return;
    }

    console.log("FINAL DATA:", selected);

    frappe.confirm(
        `Apply increment to ${selected.length} employee(s)?`,
        () => {

            frappe.call({
                method: "nafed_erp.hire_to_retire.doctype.increment_control_panel.increment_control_panel.apply_increment",
                args: {
                    employees: selected,
                    effective_date: frm.doc.effective_date,
                    increment_month: frm.doc.increment_month
                },
                freeze: true,
                freeze_message: "Applying Increment..."
            }).then(() => {

                frappe.msgprint("Increment Applied");

                frm.datatable = null;
                frm.trigger("get_employees");
            });
        }
    );
}


function set_next_basic(frm) {

    if (!frm.datatable) {
        frappe.msgprint("No data available");
        return;
    }

    let data = frm.datatable.datamanager.data;
    let check_map = frm.datatable.rowmanager.checkMap;

    let updated = 0;

    check_map.forEach((checked, idx) => {

        if (!checked) return;

        let row = data[idx];

        let current = flt(row.current_basic);
        let options = row.basic_pay_options || [];

        let next = options.find(v => flt(v) > current);

        if (next) {
            row.new_basic = next;
            updated++;
        }
    });

    // 🔥 FULL REFRESH (NO ROW REFRESH)
    frm.datatable.refresh();

    frappe.msgprint(`${updated} employee(s) updated`);
}


function export_increment(frm) {

    if (!frm.datatable) {
        frappe.msgprint("No data available");
        return;
    }

    let selected = [];
    let check_map = frm.datatable.rowmanager.checkMap;

    check_map.forEach((checked, idx) => {
        if (checked) {
            selected.push(frm.datatable.datamanager.data[idx]);
        }
    });

    if (!selected.length) {
        frappe.msgprint("Please select employees");
        return;
    }

    console.log("EXPORT DATA:", selected);

    frappe.call({
        method: "nafed_erp.hire_to_retire.doctype.increment_control_panel.increment_control_panel.export_increment_report",
        args: {
            employees: selected,
            increment_month: frm.doc.increment_month,
            effective_date: frm.doc.effective_date
        },
        freeze: true,
        freeze_message: "Generating Report..."
    }).then(r => {
        if (r.message) {
            window.open(r.message);
        }
    });
}