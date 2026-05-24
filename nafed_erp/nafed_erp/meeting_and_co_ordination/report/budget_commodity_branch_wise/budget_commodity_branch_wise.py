import frappe


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters or {})
	return columns, data


def get_columns():
	return [

		{
			"label": "Commodity",
			"fieldname": "commodity",
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

	# Grand totals (only scheme subtotals)
	grand_purchase_qty = 0
	grand_purchase_val = 0
	grand_sales_qty = 0
	grand_sales_val = 0
	grand_export_qty = 0
	grand_export = 0
	grand_profit = 0
	

	commodities = frappe.get_all("Company", pluck="name")

	for commodity in commodities:

		# Get branches for this commodity
		branch_filters = {
			"commodity": commodity,
			"status": "Approved"
		}
		if filters.get("budget_year"):
			branch_filters["budget_year"] = filters["budget_year"]

		if filters.get("branch"):
			branch_filters["branch"] = filters["branch"]
		if filters.get("commodity"):
			branch_filters["commodity"] = filters["commodity"]	

		branches = frappe.get_all(
			"Budget Entry Form",
			filters=branch_filters,
			distinct=True,
			pluck="branch"
		)

		commodity_has_data = False

		scheme_purchase_qty=0
		scheme_purchase_val=0
		scheme_sales_qty=0
		scheme_sales_val=0
		scheme_export=0
		expr_qty=0
		scheme_profit=0
		for branch in branches:

			base_filters = {
				"status": "Approved",
				"commodity": commodity,
				"branch": branch
			}

			if filters.get("budget_year"):
				base_filters["budget_year"] = filters["budget_year"]

			entries = frappe.get_all(
				"Estimated Budget Entry Form",
				filters=base_filters,
				fields=[
					"branch",
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

			# Commodity header (once)
			if not commodity_has_data:
				result.append({
					"commodity": commodity
				})
				commodity_has_data = True

			# Branch header
			# result.append({
			#     "branch": branch
			# })



			for e in entries:
				pq = e.get("budget_purchase_qty") or 0
				pv = e.get("budget_purchase_value") or 0
				sq = e.get("budget_sale_qty") or 0
				sv = e.get("budget_sale_value") or 0
				ex_q = e.get("export_qty") or 0
				ev = e.get("budget_export_value") or 0
				pr = e.get("profit") or 0

				result.append({
					"branch": e["branch"],
					"purchase_qty": pq,
					"purchase_val": pv,
					"sales_qty": sq,
					"sales_val": sv,
					"export_qty":ex_q,
					"total_export": ev,
					"total_profit": pr,
				})

				scheme_purchase_qty += pq
				scheme_purchase_val += pv
				scheme_sales_qty += sq
				scheme_sales_val += sv
				scheme_export += ev
				expr_qty += ex_q
				scheme_profit += pr

			# Scheme subtotal


			# Add to grand totals
		grand_purchase_qty += scheme_purchase_qty
		grand_purchase_val += scheme_purchase_val
		grand_sales_qty += scheme_sales_qty
		grand_sales_val += scheme_sales_val
		grand_export_qty += expr_qty
		grand_export += scheme_export
		grand_profit += scheme_profit
		if scheme_purchase_qty or scheme_purchase_val or scheme_sales_qty :
			result.append({
				"branch":      "SUB TOTAL","purchase_qty":scheme_purchase_qty,
				"purchase_val":scheme_purchase_val,"sales_qty":scheme_sales_qty,
				"sales_val":   scheme_sales_val,
				"total_export":scheme_export,
				"export_qty":expr_qty,
				"total_profit":scheme_profit,
			})
			result.append({
				"branch":      "","purchase_qty":"",
				"purchase_val":"","sales_qty":"",
				"sales_val":   "",
				"total_export":"",
				"export_qty":"",
				"total_profit":"",
			})

	if grand_purchase_qty or grand_purchase_val or grand_sales_qty or grand_sales_val:
		result.append({
			"commodity": "GRAND TOTAL",
			"purchase_qty": grand_purchase_qty,
			"purchase_val": grand_purchase_val,
			"sales_qty": grand_sales_qty,
			"sales_val": grand_sales_val,
			"export_qty": grand_export_qty,
			"total_export": grand_export,
			"total_profit": grand_profit,
		})

	return result
