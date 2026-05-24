frappe.pages['counter-mapping-page'].on_page_load = function (wrapper) {


    if (wrapper.page_loaded) {
        return;
    }
    wrapper.page_loaded = true;

    let page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'AGM Counter Dashboard',
        single_column: true
    });

    let container = $('<div></div>').appendTo(page.body);

    frappe.call({
        method: "nafed_erp.meeting_and_co_ordination.doctype.counter_mapping.counter_mapping.get_dashboard_data",
        callback: function (r) {

            if (!r.message || r.message.length === 0) {
                container.html('<p>No data found</p>');
                return;
            }

            let html = `
                <table class="table table-bordered" style="background:cornsilk">
                    <thead>
                        <tr>
                            <th>State</th>
                            <th>Counter</th>
                            <th>Alphabet Range</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
            `;

            r.message.forEach(row => {
                html += `
                    <tr>
                        <td>${row.state}</td>
                        <td>${row.counter}</td>
                        <td>${row.range}</td>
                        <td><span class="indicator green">Active</span></td>
                    </tr>
                `;
            });

            html += `
                    </tbody>
                </table>
            `;

            container.html(html);
        }
    });
};
