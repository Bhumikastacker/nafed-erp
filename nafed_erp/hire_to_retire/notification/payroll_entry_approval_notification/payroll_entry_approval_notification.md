<p style="font-size: 14px;">
    <strong>A new Payroll Entry requires your approval.</strong>
</p>

<table style="font-size: 14px; border-collapse: collapse;">
    <tr>
        <td style="padding: 4px 8px;"><strong>Payroll Entry ID:</strong></td>
        <td style="padding: 4px 8px;">{{ doc.name }}</td>
    </tr>
    
    <tr>
        <td style="padding: 4px 8px;"><strong>Posting Date:</strong></td>
        <td style="padding: 4px 8px;">{{ doc.posting_date }}</td>
    </tr>

    <tr>
        <td style="padding: 4px 8px;"><strong>Submitted By:</strong></td>
        <td style="padding: 4px 8px;">{{ doc.owner }}</td>
    </tr>
</table>


<p style="margin-top: 12px; font-size: 14px;">
    <strong>Open Document:</strong><br>
    <a href="{{ frappe.utils.get_url() }}/app/payroll-entry/{{ doc.name }}" target="_blank">
        Click here to view the Payroll Entry
    </a>
</p>
