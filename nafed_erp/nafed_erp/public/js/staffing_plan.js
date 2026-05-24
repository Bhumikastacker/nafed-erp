frappe.ui.form.off("Staffing Plan", "get_job_requisitions");
frappe.ui.form.on("Staffing Plan", {
	validate(frm) {
        if (frm.doc.from_date && frm.doc.to_date) {
            if (frm.doc.to_date < frm.doc.from_date) {
                frappe.msgprint(__('To Date cannot be earlier than From Date'));
                frappe.validated = false;
            }
        }
    },
	setup: function (frm) {
		frm.set_query("designation", "staffing_details", function () {
			let designations = [];
			(frm.doc.staffing_details || []).forEach(function (staff_detail) {
				if (staff_detail.designation) {
					designations.push(staff_detail.designation);
				}
			});
			// Filter out designations already selected in Staffing Plan Detail
			return {
				filters: [["Designation", "name", "not in", designations]],
			};
		});

		frm.set_query("department", function () {
			return {
				filters: {
					company: frm.doc.company,
				},
			};
		});
	},
	department: function(frm){
		frm.clear_table("staffing_details");
    	frm.refresh_field("staffing_details");

		frm.set_value("total_estimated_budget", 0);
	},
	get_job_requisitions: function (frm) {
		console.log("pop uppppppppppppppppppp")
		new frappe.ui.form.MultiSelectDialog({
			doctype: "Job Requisition",
			target: frm,
			date_field: "posting_date",
			add_filters_group: 1,
			setters: {
				designation: null,
				requested_by: null,
			},
			get_query() {
				let filters = {
					company: frm.doc.company,
					status: ["in", ["Open & Approved"]],
				};

				if (frm.doc.department) filters.department = frm.doc.department;

				return {
					filters: filters,
				};
			},
			action(selections) {
				const plan_name = frm.doc.__newname;
				frappe
					.call({
						method: "set_job_requisitions",
						doc: frm.doc,
						args: selections,
					})
					.then(() => {
						// hack to retain prompt name that gets lost on frappe.call
						frm.doc.__newname = plan_name;
						refresh_field("staffing_details");
						let total = 0;
						(frm.doc.staffing_details || []).forEach(row => {
							total += flt(row.total_estimated_cost) || 0;
						});

						frm.set_value("total_estimated_budget", total);
					});
				cur_dialog.hide();
			},
		});
	},
});

