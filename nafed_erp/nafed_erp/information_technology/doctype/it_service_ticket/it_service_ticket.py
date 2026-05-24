import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime, add_to_date

class ITServiceTicket(Document):
    def before_insert(self):
        if not self.raised_by:
            emp = frappe.db.get_value(
                "Employee",
                {"user_id": frappe.session.user},
                "name"
            )
            if emp:
                self.raised_by = emp
                
    def on_update(self):
        if self.workflow_state != "Submitted":
            return
        if self.assigned_to:
            return
        self.created_on = now_datetime()
        self.status = "New"
        rule = frappe.db.get_value(
            "IT Ticket Routing Rule",
            {
                "category": self.category,
                "sub_category": self.sub_category
            },
            ["support_group"],
            as_dict=True
        )

        if not rule or not rule.support_group:
            frappe.throw(
                "Routing Rule or Support Group not defined for this Category/Sub-Category"
            )
        team_members = frappe.get_all(
            "HD Team Member",
            filters={
                "parent": rule.support_group,
                "parenttype": "HD Team",
                "parentfield": "users"
            },
            fields=["user"]
        )
        agents = [m.user for m in team_members if m.user]
        if not agents:
            frappe.throw(
                f"No users configured in HD Team {rule.support_group}"
            )
        assigned_agent = get_next_agent(rule.support_group, agents)
        self.assigned_group = rule.support_group
        self.assigned_to = assigned_agent
        self.sla_target = calculate_sla(self.priority)
        self.status = "Open"
        self.db_update()
        # notify_agent(self)
        
    def validate(self):
        user = frappe.session.user
        roles = frappe.get_roles(user)

        if "IT Ticket Agent" in roles:
            if self.assigned_to != user:
                frappe.throw("You are not assigned to this ticket.")

        if "IT Ticket User" in roles:
            if self.raised_by_user != user:
                frappe.throw("You can only view your own tickets.")

            if self.workflow_state not in ["Resolved"]:
                frappe.throw("You can only view this ticket.")


def calculate_sla(priority):
    """
    Calculate SLA target datetime based on priority
    """
    sla_hours = {
        "Low": 48,
        "Medium": 24,
        "High": 8,
        "Critical": 4
    }

    return add_to_date(
        now_datetime(),
        hours=sla_hours.get(priority, 24)
    )

def get_next_agent(team_name, agents):
    
    cache_key = f"it_ticket_rr::{team_name}"

    last_agent = frappe.cache().get_value(cache_key)

    if last_agent in agents:
        idx = agents.index(last_agent)
        next_agent = agents[(idx + 1) % len(agents)]
    else:
        next_agent = agents[0]

    frappe.cache().set_value(cache_key, next_agent)

    return next_agent


# def notify_agent(ticket):
#     """
#     Email + In-App notification to assigned agent
#     """
#     frappe.sendmail(
#         recipients=[ticket.assigned_to],
#         subject=f"New IT Ticket Assigned: {ticket.name}",
#         message=f"""
#         <p>You have been assigned a new IT Service Ticket.</p>

#         <ul>
#             <li><b>Ticket ID:</b> {ticket.name}</li>
#             <li><b>Status:</b> {ticket.status}</li>
#             <li><b>Category:</b> {ticket.category}</li>
#             <li><b>Priority:</b> {ticket.priority}</li>
#             <li><b>SLA Target:</b> {ticket.sla_target}</li>
#         </ul>
#         """
#     )
#     frappe.publish_realtime(
#         "notification",
#         {
#             "message": f"New IT Ticket {ticket.name} assigned to you",
#             "reference_doctype": ticket.doctype,
#             "reference_name": ticket.name
#         },
#         user=ticket.assigned_to
#     )
@frappe.whitelist()
def get_permission_query_conditions(user):
    if not user:
        user = frappe.session.user

    roles = frappe.get_roles(user)

    if "IT Ticket Agent" in roles:
        return f"`tabIT Service Ticket`.assigned_to = '{user}'"

    if "IT Ticket User" in roles:
        return f"`tabIT Service Ticket`.raised_by_user = '{user}'"

    return None
