frappe.ui.form.on('Interview Detail', {
	interviewer(frm, cdt, cdn) {
		const row = locals[cdt][cdn];

		let count = 0;
		(frm.doc.interview_details || []).forEach(r => {
			if (r.interviewer === row.interviewer) {
				count++;
			}
		});

		if (count > 1) {
			frappe.msgprint({
				title: __('Duplicate Interviewer'),
				message: __('This interviewer is already added.'),
				indicator: 'red'
			});
			frappe.model.set_value(cdt, cdn, 'interviewer', '');
		}
	}
});
