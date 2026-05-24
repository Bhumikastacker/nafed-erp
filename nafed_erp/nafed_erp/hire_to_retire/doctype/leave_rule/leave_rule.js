frappe.ui.form.on("Leave Rule", {
    refresh(frm) {

        let uncompensated_html = `
            <div style="
                padding: 12px;
                border: 1px solid #ccc;
                border-radius: 8px;
                background: #f9fbfd;
                color: #222;
                font-size: 13px;
                line-height: 1.6;
            ">
                <h4 style="margin-bottom: 10px; font-size: 14px; font-weight: bold; color: #0a3d62;">
                    Uncompensated Late Entry Count — Rule Description
                </h4>

                <p>
                    This rule is used when an employee <b>arrives late</b> and also 
                    <b>leaves before the scheduled shift end time</b>.  
                    In such cases, the system applies a <b>leave deduction</b> 
                    based on the settings configured in this Leave Rule.
                </p>

                <p>
                    <b>How it works:</b>
                </p>
                <ul style="padding-left: 18px; margin: 0;">
                    <li>
                        The employee checks in <b>after</b> the shift start tolerance 
                        (Late Entry).
                    </li>
                    <li>
                        AND the employee checks out <b>before</b> the required Uncompensated 
                        shift end time defined in Shift Type.
                    </li>
                    <li>
                        → When both conditions occur on the same day, it counts as 
                        <b>1 violation</b>.
                    </li>
                    <li>
                        When the number of violations reaches the configured limit 
                        (e.g., <b>2 violations</b>), a <b>leave deduction is triggered</b>.
                    </li>
                </ul>

                <p style="margin-top: 10px; font-size: 12px; color: #555;">
                    <b>Example:</b><br>
                    Shift Time: 9:00 AM – 6:00 PM<br>
                    Allowed Violations: <b>2</b><br><br>

                    Day 1: Employee comes at 9:30 AM <i>(late)</i> and leaves at 5:30 PM <i>(early)</i> → 1 violation.<br>
                    Day 2: Same pattern happens again → <b>2nd violation</b>.<br><br>

                    <b>Result:</b> Leave deduction applies after the 2nd violation.
                </p>
            </div>
        `;

        if (frm.fields_dict.rules_description) {
            frm.fields_dict.rules_description.$wrapper.html(uncompensated_html);
        }
    }
});
