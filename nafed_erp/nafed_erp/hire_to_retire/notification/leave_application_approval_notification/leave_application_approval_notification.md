<p>Dear {{ doc.leave_approver_name }},</p>

<p>A leave request has been submitted with the following details:</p>

<p>
Employee ID: {{ doc.employee }}<br>
Employee Name: {{ doc.employee_name }}<br>
From Date: {{ doc.from_date }}<br>
To Date: {{ doc.to_date }}<br>
Total Leave Days: {{ doc.total_leave_days }}<br>
Posting Date: {{ doc.posting_date }}<br>
Current Status: {{ doc.status }}
</p>

<p>
Please review the request and take the necessary action.
</p>

<p style="margin-top: 12px; font-size: 14px;">
    <strong>Open Document:</strong><br>
    <a href="{{ frappe.utils.get_url() }}/app/leave-application/{{ doc.name }}" target="_blank">
        Click here to view the Leave Application
    </a>
</p>


<p>
Regards,<br>
{{ doc.company }}
</p>
