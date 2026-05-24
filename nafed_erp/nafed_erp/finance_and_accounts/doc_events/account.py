import frappe

@frappe.whitelist()
def account_has_balance(account):
    """
    Returns True if the account OR any child account has balance.
    Works for group & non-group accounts.
    """

    # Get this account details
    acc = frappe.get_doc("Account", account)

    # -------------------------
    # 1️⃣ Get all child accounts
    # -------------------------
    if acc.is_group:
        children = frappe.db.get_list(
            "Account",
            filters={
                "lft": (">=", acc.lft),
                "rgt": ("<=", acc.rgt),
                "company": acc.company
            },
            pluck="name"
        )
    else:
        children = [account]

    if not children:
        return False

    # -------------------------
    # 2️⃣ Sum GL Entries for all accounts
    # -------------------------
    totals = frappe.db.sql(
        """
        SELECT 
            IFNULL(SUM(debit), 0) AS total_debit,
            IFNULL(SUM(credit), 0) AS total_credit
        FROM `tabGL Entry`
        WHERE account IN %(accounts)s
        """,
        {"accounts": children},
        as_dict=True
    )[0]

    # -------------------------
    # 3️⃣ Calculate balance
    # -------------------------
    balance = totals.total_debit - totals.total_credit

    return abs(balance) > 0
