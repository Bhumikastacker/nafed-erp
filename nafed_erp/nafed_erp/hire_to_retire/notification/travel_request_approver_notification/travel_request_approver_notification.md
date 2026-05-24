<p style="font-size: 14px;">
    <strong>A new Travel Request requires your approval.</strong>
</p>

<table style="font-size: 14px; border-collapse: collapse;">
    <tr>
        <td style="padding: 4px 8px;"><strong>Request ID:</strong></td>
        <td style="padding: 4px 8px;">{{ doc.name }}</td>
    </tr>
    
    <tr>
        <td style="padding: 4px 8px;"><strong>Submission Date:</strong></td>
        <td style="padding: 4px 8px;">{{ doc.custom_submission_date }}</td>
    </tr>

    <tr>
        <td style="padding: 4px 8px;"><strong>Total Travel Duration:</strong></td>
        <td style="padding: 4px 8px;">{{ doc.custom_total_travel_duration }}</td>
    </tr>

    <tr>
        <td style="padding: 4px 8px;"><strong>Total Amount:</strong></td>
        <td style="padding: 4px 8px;">{{ doc.custom_total_travel_amount }}</td>
    </tr>

    <tr>
        <td style="padding: 4px 8px;"><strong>Submitted By:</strong></td>
        <td style="padding: 4px 8px;">{{ doc.employee_name }}</td>
    </tr>
</table>

<h3 style="margin-top: 20px; font-size:16px; color:#1f7bd4;">Travel Itinerary</h3>

<table role="presentation" cellpadding="8" cellspacing="0" width="100%" 
       style="border-collapse: collapse; border:1px solid #ddd; font-size:14px;">
    
    <thead>
        <tr style="background:#f0f4f7; text-align:left;">
            <th style="border:1px solid #ddd;">From</th>
            <th style="border:1px solid #ddd;">To</th>
            <th style="border:1px solid #ddd;">Departure</th>
            <th style="border:1px solid #ddd;">Arrival</th>
            <th style="border:1px solid #ddd;">Duration</th>
        </tr>
    </thead>

    <tbody>
        {% for row in doc.itinerary %}
        <tr>
            <td style="border:1px solid #ddd;">{{ row.travel_from }}</td>
            <td style="border:1px solid #ddd;">{{ row.travel_to }}</td>
            <td style="border:1px solid #ddd;">{{ row.departure_date }}</td>
            <td style="border:1px solid #ddd;">{{ row.arrival_date }}</td>
            <td style="border:1px solid #ddd;">{{ row.custom_travel_duration }}</td>
        </tr>
        {% endfor %}
    </tbody>

</table>


<p style="margin-top: 12px; font-size: 14px;">
    <strong>Open Document:</strong><br>
    <a href="{{ frappe.utils.get_url() }}/app/travel-request/{{ doc.name }}" target="_blank">
        Click here to view the Travel Request
    </a>
</p>
