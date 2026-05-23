import frappe
from frappe.model.mapper import get_mapped_doc
from frappe.utils import nowdate, flt
from erpnext.stock.utils import get_stock_balance


def create_material_request_from_sales_order(source_name):
    """
    Creates Material Request from Sales Order.
    Only includes items with insufficient stock quantity.
    """

    def set_missing_values(source, target):
        target.material_request_type = "Purchase"
        target.company = source.company
        target.schedule_date = nowdate()

    def update_item(source_item, target_item, source_parent):
        """
        Updates Material Request Item with data from Sales Order Item.
        Checks stock availability and calculates required quantity.
        """
        # Get the warehouse from Sales Order Item or use company's default warehouse
        warehouse = source_item.warehouse or frappe.get_cached_value(
            "Company", source_parent.company, "default_warehouse"
        )
        
        if not warehouse:
            # If no warehouse is set, include the item with full quantity
            required_qty = source_item.qty
        else:
            # Get current stock balance for the item in the warehouse
            available_qty = get_stock_balance(
                item_code=source_item.item_code,
                warehouse=warehouse,
                posting_date=nowdate()
            )
            
            # Calculate how much quantity is needed
            required_qty = flt(source_item.qty) - flt(available_qty)
        
        # Only include items that have insufficient stock (required_qty > 0)
        if required_qty > 0:
            target_item.schedule_date = source_item.delivery_date or nowdate()
            target_item.sales_order = source_parent.name
            target_item.sales_order_item = source_item.name
            target_item.qty = required_qty  # Request only the deficit quantity
            target_item.uom = source_item.uom
            target_item.item_code = source_item.item_code
            target_item.stock_uom = source_item.stock_uom
            target_item.conversion_factor = source_item.conversion_factor
            target_item.warehouse = warehouse
        else:
            # Return None to exclude this item from Material Request
            return None

    doc = get_mapped_doc(
        "Sales Order",
        source_name,
        {
            "Sales Order": {
                "doctype": "Material Request",
            },
            "Sales Order Item": {
                "doctype": "Material Request Item",
                "postprocess": update_item,
                # Filter to exclude items with None (sufficient stock)
                "condition": lambda doc: doc.qty > 0,
            },
        },
        None,
        set_missing_values,
    )

    # Remove any empty items (items that returned None from update_item)
    doc.items = [item for item in doc.items if item.item_code]

    # Only create Material Request if there are items that need to be purchased
    if not doc.items:
        frappe.msgprint(
            "All items in the Sales Order have sufficient stock. No Material Request created.",
            alert=True
        )
        return None

    doc.insert(ignore_permissions=True)

    # Update Sales Order Items with reverse link
    for mr_item in doc.items:
        if mr_item.sales_order_item:
            frappe.db.set_value(
                "Sales Order Item",
                mr_item.sales_order_item,
                {
                    "material_request": doc.name,
                    "material_request_item": mr_item.name
                },
                update_modified=False
            )

    frappe.msgprint(
        f"Material Request {doc.name} created successfully for items with insufficient stock.",
        alert=True
    )
    
    return doc.name


def sales_order_on_submit(doc, method):
    """
    Hook function triggered when Sales Order is submitted.
    Creates Material Request only for items with insufficient stock.
    """

        
        # Check if Material Request already exists for this Sales Order
    existing_mr = frappe.db.exists(
            "Material Request Item",
            {
                "sales_order": doc.name
            }
        )

    if not existing_mr:
            create_material_request_from_sales_order(doc.name)