frappe.ui.form.on('Bank Payment', {
	refresh: function(frm) {

		if(frm.doc.docstatus==1) {
					frm.add_custom_button(__('Ledger'), function() {
						frappe.route_options = {
							"voucher_no": "J" + frm.doc.name,
							"from_date": frm.doc.posting_date,
							"to_date": frm.doc.posting_date,
							"company": frm.doc.company,
							group_by_voucher: 0
						};
						frappe.set_route("query-report", "General Ledger");
					}, "fa fa-table");
				}

	}
});
