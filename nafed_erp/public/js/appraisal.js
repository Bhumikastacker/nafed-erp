// by mayuri
// Validation to check if Appraisal Cycle is started before saving
frappe.ui.form.on("Appraisal", {
	validate: function(frm) {
		if (frm.doc.appraisal_cycle) {
			return frappe.db.get_value("Appraisal Cycle", frm.doc.appraisal_cycle, "status")
				.then(r => {
					if (r.message && r.message.status === "Not Started") {
						frappe.msgprint({
							title: __("Appraisal Cycle Not Started"),
							indicator: "orange",
							message: __("Please start the Appraisal Cycle before assigning it to an employee.")
						});
						frappe.validated = false;
					}
				});
		}
	}
});