<p style="font-size: 14px;">
    <strong>A new Project Activity Progress log requires your approval.</strong>
</p>

<table style="font-size: 14px; border-collapse: collapse;">
    <tr>
        <td style="padding: 4px 8px;"><strong>Project Activity Progress ID:</strong></td>
        <td style="padding: 4px 8px;">{{ doc.name }}</td>
    </tr>
    <tr>
        <td style="padding: 4px 8px;"><strong>Activity ID:</strong></td>
        <td style="padding: 4px 8px;">{{ doc.activity }}</td>
    </tr>
    <tr>
        <td style="padding: 4px 8px;"><strong>Milestone ID:</strong></td>
        <td style="padding: 4px 8px;">{{ doc.milestone }}</td>
    </tr>
    <tr>
        <td style="padding: 4px 8px;"><strong>Project ID:</strong></td>
        <td style="padding: 4px 8px;">{{ doc.project }}</td>
    </tr>
    <tr>
        <td style="padding: 4px 8px;"><strong>Approval Status:</strong></td>
        <td style="padding: 4px 8px;">{{ doc.approval_status }}</td>
    </tr>
    <tr>
        <td style="padding: 4px 8px;"><strong>Creation Date:</strong></td>
        <td style="padding: 4px 8px;">{{ doc.creation }}</td>
    </tr>
    <tr>
        <td style="padding: 4px 8px;"><strong>Division:</strong></td>
        <td style="padding: 4px 8px;">{{ doc.division }}</td>
    </tr>
    <tr>
        <td style="padding: 4px 8px;"><strong>Activity Actual Start Date:</strong></td>
        <td style="padding: 4px 8px;">{{ doc.actual_start_date }}</td>
    </tr>
    <tr>
        <td style="padding: 4px 8px;"><strong>Activity Actual End Date:</strong></td>
        <td style="padding: 4px 8px;">{{ doc.actual_end_date }}</td>
    </tr>
    <tr>
        <td style="padding: 4px 8px;"><strong>Activity Progress:</strong></td>
        <td style="padding: 4px 8px;">{{ doc.activity_progress_percent }}</td>
    </tr>
    <tr>
        <td style="padding: 4px 8px;"><strong>Created By:</strong></td>
        <td style="padding: 4px 8px;">{{ doc.owner }}</td>
    </tr>

</table>

<p style="margin-top: 12px; font-size: 14px;">
    <strong>Open Document:</strong><br>
    <a href="{{ frappe.utils.get_url() }}/app/activity-progress-log/{{ doc.name }}" target="_blank">
        Click here to view the Project Activity Progress Log
    </a>
</p>
