import frappe
from frappe.model.document import Document
from frappe.utils import getdate, today

class BoardMeeting(Document):

	def validate(self):
		self.validate_child_members()
		self.validate_duplicate_meeting()
		if self.meeting_date and getdate(self.meeting_date) < getdate(today()):
			frappe.throw("Meeting date cannot be in the past")
		print("selfdddddddddddd", self)  

		if self.workflow_state == 'Agenda Submitted':
			existing = frappe.db.exists(
			"Meeting Agenda",
			
			)
			if existing:
				frappe.throw("Agenda already exists for this Meeting")



		
	def validate_duplicate_meeting(self):
		if not self.meeting_date or not self.meeting_time:
		    return

		existing = frappe.db.exists(
		    self.doctype,
		    {
		        "meeting_date": self.meeting_date,
		        "meeting_time": self.meeting_time,
		        "meeting_type": self.meeting_type,
		        "name": ["!=", self.name]  # important for edit case
		    }
		)

		if existing:
		    frappe.throw(
		        f"A meeting is already scheduled on {self.meeting_date} at {self.meeting_time}"
		    )

			  


	def validate_child_members(self):
		if not self.attendance:
		    return

		attendance_list = []

		for row in self.attendance:  # replace with your actual child table fieldname
		    
		    # 1️⃣ Check child member not equal to parent member
		    
		    if row.email in attendance_list:
		        frappe.throw(
		            f"Row #{row.idx}: Member ID {row.email} is already added in Attendance table"
		        )

		    attendance_list.append(row.board_member)
	
	

