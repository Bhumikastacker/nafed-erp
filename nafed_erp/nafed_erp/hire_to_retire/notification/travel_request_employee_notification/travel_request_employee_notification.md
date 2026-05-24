<p style="font-size: 14px;">
    Dear {{ doc.employee_name }},
</p>

<p style="font-size: 14px;">
    Your Travel Request <strong>{{ doc.name }}</strong> has been updated.
</p>

<table role="presentation" cellpadding="6" cellspacing="0" width="100%" 
       style="border-collapse: collapse; font-size:14px; margin-bottom: 16px;">
    <tr>
        <td style="color:#555;">Status:</td>
        <td><strong>{{ doc.custom_status }}</strong></td>
    </tr>
    <tr>
        <td style="color:#555;">Submitted On:</td>
        <td><strong>{{ doc.custom_submission_date }}</strong></td>
    </tr>
    <tr>
        <td style="color:#555; vertical-align: top;">Comments:</td>
        <td>
            {% if doc.custom_comments %}
                {{ doc.custom_comments }}
            {% else %}
                <em>No comments added.</em>
            {% endif %}
        </td>
    </tr>
</table>

<!-- Itinerary Table -->
<h3 style="margin-top:20px; color:#1f7bd4; font-size:16px;">Travel Itinerary</h3>

<table role="presentation" cellpadding="8" cellspacing="0" width="100%"
       style="border-collapse: collapse; border:1px solid #ddd; font-size:14px;">
    <thead>
        <tr style="background:#f0f4f7;">
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

<p style="margin-top: 20px;">
    <a href="{{ frappe.utils.get_url() }}/app/travel-request/{{ doc.name }}" 
       target="_blank"
       style="display:inline-block;padding:10px 16px;border-radius:6px;
              text-decoration:none;background:#1f7bd4;color:#ffffff;font-weight:600;">
        Open Travel Request
    </a>
</p>
