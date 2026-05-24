// Copyright (c) 2025, CSM Technologies Pvt Ltd and contributors
// For license information, please see license.txt
console.log("LTC Report JS loaded");


frappe.query_reports["LTC Report"] = {
	formatter: function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);

		if (!data) return value;

		// -------------------------
		// Advance Payment Status
		// -------------------------
		if (column.fieldname === "advance_payment_status") {
			return get_status_indicator(value);
		}

		// -------------------------
		// Expense Payment Status
		// -------------------------
		if (column.fieldname === "expense_payment_status") {
			return get_status_indicator(value);
		}

		return value;
	}
};

function get_status_indicator(status) {
	if (!status) return "";

	let color = "gray";

	if (status === "Paid") {
		color = "blue";
	} else if (status === "Partially Paid") {
		color = "orange";
	} else if (status === "Not Paid") {
		color = "red";
	} else if (status === "Not Initiated") {
		color = "gray";
	}

	return `<span class="indicator ${color}">${status}</span>`;
}