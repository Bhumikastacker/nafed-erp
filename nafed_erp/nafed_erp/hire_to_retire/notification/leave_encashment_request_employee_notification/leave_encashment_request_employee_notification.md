Dear Approver,<br><br>

A new <b>Leave Encashment Request</b> has been submitted by
<b>{{ doc.employee_name }}</b>.<br><br>

<b>Status:</b> {{ doc.status }}<br><br>
<b>Request Date:</b> {{ doc.request_date }}<br><br>
<b>Leave Days to Encash:</b> {{ doc.leave_days_to_encash }}<br><br>

You can review the request here:<br>
<a href="{{ frappe.utils.get_url() }}/app/leave-encashment-request/{{ doc.name }}" target="_blank">
Open Request
</a><br><br>

Thank you.
