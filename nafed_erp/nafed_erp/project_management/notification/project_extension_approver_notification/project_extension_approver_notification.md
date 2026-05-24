<p style="font-size: 14px;">
    <strong>A new Project Extension Request requires your approval.</strong>
</p>

<table style="font-size: 14px; border-collapse: collapse;">
    <tr>
        <td style="padding: 4px 8px;"><strong>Project Extension Request ID:</strong></td>
        <td style="padding: 4px 8px;">{{ doc.name }}</td>
    </tr>
    <tr>
        <td style="padding: 4px 8px;"><strong>Project ID:</strong></td>
        <td style="padding: 4px 8px;">{{ doc.project }}</td>
    </tr>
    <tr>
        <td style="padding: 4px 8px;"><strong>Project Name:</strong></td>
        <td style="padding: 4px 8px;">{{ doc.project_name }}</td>
    </tr>
    <tr>
        <td style="padding: 4px 8px;"><strong>Approval Status:</strong></td>
        <td style="padding: 4px 8px;">{{ doc.status }}</td>
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
        <td style="padding: 4px 8px;"><strong>Project Old End Date:</strong></td>
        <td style="padding: 4px 8px;">{{ doc.project_old_end_date }}</td>
    </tr>
    <tr>
        <td style="padding: 4px 8px;"><strong>Project New End Date:</strong></td>
        <td style="padding: 4px 8px;">{{ doc.project_new_end_date }}</td>
    </tr>
    <tr>
        <td style="padding: 4px 8px;"><strong>Additional_cost:</strong></td>
        <td style="padding: 4px 8px;">{{ doc.additional_cost }}</td>
    </tr>
    <tr>
        <td style="padding: 4px 8px;"><strong>Justification:</strong></td>
        <td style="padding: 4px 8px;">{{ doc.justification }}</td>
    </tr>
    <tr>
        <td style="padding: 4px 8px;"><strong>Created By:</strong></td>
        <td style="padding: 4px 8px;">{{ doc.owner }}</td>
    </tr>

</table>

<p style="margin-top: 12px; font-size: 14px;">
    <strong>Open Document:</strong><br>
    <a href="{{ frappe.utils.get_url() }}/app/project-extension-request/{{ doc.name }}" target="_blank">
        Click here to view the Project Extension Request
    </a>
</p>
