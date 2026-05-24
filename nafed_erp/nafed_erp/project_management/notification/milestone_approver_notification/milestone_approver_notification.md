<p style="font-size: 14px;">
    <strong>A new Milestone requires your approval.</strong>
</p>

<table style="font-size: 14px; border-collapse: collapse;">
    <tr>
        <td style="padding: 4px 8px;"><strong>Milestone ID:</strong></td>
        <td style="padding: 4px 8px;">{{ doc.name }}</td>
    </tr>
    <tr>
        <td style="padding: 4px 8px;"><strong>Creation Date:</strong></td>
        <td style="padding: 4px 8px;">{{ doc.creation }}</td>
    </tr>
    <tr>
        <td style="padding: 4px 8px;"><strong>Approval Status:</strong></td>
        <td style="padding: 4px 8px;">{{ doc.custom_approval_status }}</td>
    </tr>
    <tr>
        <td style="padding: 4px 8px;"><strong>Division:</strong></td>
        <td style="padding: 4px 8px;">{{ doc.custom_division }}</td>
    </tr>
    <tr>
        <td style="padding: 4px 8px;"><strong>Expected Start Date:</strong></td>
        <td style="padding: 4px 8px;">{{ doc.exp_start_date }}</td>
    </tr>
    <tr>
        <td style="padding: 4px 8px;"><strong>Expected End Date:</strong></td>
        <td style="padding: 4px 8px;">{{ doc.exp_end_date }}</td>
    </tr>
    <tr>
        <td style="padding: 4px 8px;"><strong>Estimated Cost:</strong></td>
        <td style="padding: 4px 8px;">{{ doc.custom_estimated_cost }}</td>
    </tr>
    <tr>
        <td style="padding: 4px 8px;"><strong>Technical Partner:</strong></td>
        <td style="padding: 4px 8px;">{{ doc.custom_technical_partner }}</td>
    </tr>
    <tr>
        <td style="padding: 4px 8px;"><strong>Created By:</strong></td>
        <td style="padding: 4px 8px;">{{ doc.owner }}</td>
    </tr>

</table>

<p style="margin-top: 12px; font-size: 14px;">
    <strong>Open Document:</strong><br>
    <a href="{{ frappe.utils.get_url() }}/app/task/{{ doc.name }}" target="_blank">
        Click here to view the Milestone
    </a>
</p>
