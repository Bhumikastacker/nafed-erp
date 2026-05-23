import frappe


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters or {})
	return columns, data


def get_columns():
	return [

		{
			"label": "Region/Zone",
			"fieldname": "region",
			"fieldtype": "Data",
			"width": 160
		},{
			"label":"Branch","fieldname":"branch","fieldtype":"Data",
			"width":160},

		# PURCHASE
		{
			"label": "Purchase Qty",
			"fieldname": "purchase_qty",
			# "fieldtype": "Float",
			"width": 110
		},
		{
			"label": "Purchase Value",
			"fieldname": "purchase_val",
			# "fieldtype": "Currency",
			"width": 130
		},

		# SALES
		{
			"label": "Sales Qty",
			"fieldname": "sales_qty",
			# "fieldtype": "Float",
			"width": 110
		},
		{
			"label": "Sales Value",
			"fieldname": "sales_val",
			# "fieldtype": "Float",
			"width": 130
		},{
			"label":"IMP/Exp Qty","fieldname":"export_qty",# "fieldtype": "Float",
			"width":110},
		# EXPORT / PROFIT (unchanged)
		{
			"label": "Import / Export",
			"fieldname": "total_export",
			# "fieldtype": "Float",
			"width": 140
		},
		{
			"label": "Profit",
			"fieldname": "total_profit",
			# "fieldtype": "Float",
			"width": 130
		}
	]







def get_data(filters):
	result = []

	# GRAND TOTALS
	grand_purchase_qty = 0
	grand_purchase_val = 0
	grand_sales_qty = 0
	grand_sales_val = 0
	grand_export_qty = 0
	grand_export = 0
	grand_profit = 0

	zones = frappe.get_all("Zone", pluck="name")

	for region in zones:

		# REGION TOTALS
		region_purchase_qty = 0
		region_purchase_val = 0
		region_sales_qty = 0
		region_sales_val = 0
		region_export_qty = 0
		region_export = 0
		region_profit = 0

		branch_filters = {
			"region": region,
			"status": "Approved"
		}

		if filters.get("budget_year"):
			branch_filters["budget_year"] = filters["budget_year"]

		if filters.get("branch"):
			branch_filters["branch"] = filters["branch"]

		branches = frappe.get_all(
			"Estimated Budget Entry Form",
			filters=branch_filters,
			distinct=True,
			pluck="branch"
		)
		print("ddddddddddddddddddd", region, branches)
		region_has_data = False

		for branch in branches:

			base_filters = {
				"status": "Approved",
				"region": region,
				"branch": branch
			}

			if filters.get("budget_year"):
				base_filters["budget_year"] = filters["budget_year"]

			entries = frappe.get_all(
				"Estimated Budget Entry Form",
				filters=base_filters,
				fields=[
					"budget_purchase_qty",
					"budget_purchase_value",
					"budget_sale_qty",
					"budget_sale_value",
					"export_qty",
					"budget_export_value",
					"profit",
				]
			)

			if not entries:
				continue

			# REGION HEADER (once)
			if not region_has_data:
				result.append({"region": region})
				region_has_data = True

			# 🔹 BRANCH TOTALS (IMPORTANT)
			b_pq = b_pv = b_sq = b_sv = b_exq = b_ev = b_pr = 0
			print("aaaaaaaaaaaaaaaaaaaaaaaa", region,entries)
			for e in entries:

				b_pq += e.get("budget_purchase_qty") or 0
				b_pv += e.get("budget_purchase_value") or 0
				b_sq += e.get("budget_sale_qty") or 0
				b_sv += e.get("budget_sale_value") or 0
				b_exq += e.get("export_qty") or 0
				b_ev += e.get("budget_export_value") or 0
				b_pr += e.get("profit") or 0

			# ✅ APPEND ONLY ONCE PER BRANCH
			result.append({
				"branch": branch,
				"purchase_qty": b_pq,
				"purchase_val": b_pv,
				"sales_qty": b_sq,
				"sales_val": b_sv,
				"export_qty": b_exq,
				"total_export": b_ev,
				"total_profit": b_pr,
			})

			# REGION TOTALS
			region_purchase_qty += b_pq
			region_purchase_val += b_pv
			region_sales_qty += b_sq
			region_sales_val += b_sv
			region_export_qty += b_exq
			region_export += b_ev
			region_profit += b_pr

		# REGION SUB TOTAL
		if region_has_data:
			result.append({
				"branch": "SUB TOTAL",
				"purchase_qty": region_purchase_qty,
				"purchase_val": region_purchase_val,
				"sales_qty": region_sales_qty,
				"sales_val": region_sales_val,
				"export_qty": region_export_qty,
				"total_export": region_export,
				"total_profit": region_profit,
			})
			
			
			result.append({
				"branch": "",
				"purchase_qty": "",
				"purchase_val": "",
				"sales_qty": "",
				"sales_val": "",
				"export_qty": "",
				"total_export": "",
				"total_profit": "",
			})


			# GRAND TOTAL
			grand_purchase_qty += region_purchase_qty
			grand_purchase_val += region_purchase_val
			grand_sales_qty += region_sales_qty
			grand_sales_val += region_sales_val
			grand_export_qty += region_export_qty
			grand_export += region_export
			grand_profit += region_profit

	# GRAND TOTAL ROW
	if grand_purchase_qty or grand_purchase_val or grand_sales_qty:
		result.append({
			"region": "GRAND TOTAL",
			"purchase_qty": grand_purchase_qty,
			"purchase_val": grand_purchase_val,
			"sales_qty": grand_sales_qty,
			"sales_val": grand_sales_val,
			"export_qty": grand_export_qty,
			"total_export": grand_export,
			"total_profit": grand_profit,
		})

	return result
