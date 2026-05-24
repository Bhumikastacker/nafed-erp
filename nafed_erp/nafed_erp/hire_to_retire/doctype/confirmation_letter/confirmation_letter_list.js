frappe.listview_settings['Confirmation Letter'] = {
    onload(listview) {
        listview.page.add_inner_button(__('Bulk Print PDF'), () => {
            const selected = listview.get_checked_items();

            if (!selected.length) {
                frappe.msgprint(__('Please select at least one document.'));
                return;
            }

            const docnames = selected.map(d => d.name);

            // Generate PDF and download
            const url = frappe.urllib.get_full_url(
                "/api/method/nafed_erp.hire_to_retire.doctype.confirmation_letter.confirmation_letter.bulk_print"
                + "?docnames=" + encodeURIComponent(JSON.stringify(docnames))
            );

            window.open(url);
        });
    }
};
