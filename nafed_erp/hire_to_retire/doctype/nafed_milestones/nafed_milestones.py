# Copyright (c) 2025, CSM Technologies Pvt Ltd and contributors
# For license information, please see license.txt
from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class NafedMilestones(Document):
    def validate(self):
     
        skills = []
        
        if not hasattr(self, 'table_nxqn') or not self.table_nxqn:
            return
        
        for row in self.table_nxqn:
            if not row.skill:
                continue
            
            if row.skill in skills:
                frappe.throw(f"Duplicate Skill not allowed: {row.skill}")
            
            skills.append(row.skill)



