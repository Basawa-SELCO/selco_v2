/*To set naming series when branch is choosen for the first time */
cur_frm.add_fetch("selco_branch", "selco_receipt_naming_series", "naming_series"); 

frappe.ui.form.on("Journal Entry", "validate", function(frm) {
	if (frappe.user_roles.indexOf("SELCO Lead Accountant")!=-1 && cur_frm.doc.voucher_type=="Write Off Entry") {
		frappe.throw("You are not allowed to raise the journal entry of type write off!!");
	}
});


frappe.ui.form.on("Journal Entry", "onload_post_render", function(frm) {
	if (!cur_frm.doc.__islocal) {
	//frappe.model.add_child(cur_frm.doc, "Journal Entry Account", 'accounts')
	//refresh_field("accounts");
		cur_frm.set_df_property("voucher_type", "read_only", true);
	}
});

frappe.ui.form.on("Journal Entry", "voucher_type", function(frm, cdt, cdn) {
	console.log("voucher type");
	
	if(cur_frm.doc.voucher_type == "Payment Entry - HO - SBI" && cur_frm.doc.selco_branch == "Head Office")
	{
	cur_frm.doc.naming_series = "SBI/HO/17-18/";
	console.log("SBI");
	refresh_field("naming_series");
	}
	else if (cur_frm.doc.voucher_type == "Journal Entry - HO - FD" && cur_frm.doc.selco_branch == "Head Office")   
	{
	cur_frm.doc.naming_series = "FD/HO/17-18/";
	} 
	else if (cur_frm.doc.voucher_type == "Opening Entry - HO - SELCO" && cur_frm.doc.selco_branch == "Head Office")   
	{
	cur_frm.doc.naming_series = "OPNS/HO/17-18/";
	} 

	if(cur_frm.doc.voucher_type == "Commission Journal" && cur_frm.doc.selco_branch == "Head Office")
	{
		cur_frm.doc.naming_series = "CJ/HO/17-18/";
		refresh_field("naming_series");
	}

	if (frm.doc.voucher_type == "Contra Entry") {
	    frm.doc.naming_series = frappe.db.get_value("Branch",frm.doc.selco_branch,"selco_contra_naming_series")
	}
	if (frm.doc.voucher_type == "Cash Payment") {
	    frm.doc.naming_series = frappe.db.get_value("Branch",frm.doc.selco_branch,"selco_cash_payment_naming_series")
	}
	if (frm.doc.voucher_type == "Debit Note") {
	    frm.doc.naming_series = frappe.db.get_value("Branch",frm.doc.selco_branch,"selco_debit_note__naming_series")
	}
	if (frm.doc.voucher_type == "Credit Note") {
	    frm.doc.naming_series = frappe.db.get_value("Branch",frm.doc.selco_branch,"selco_credit_note_naming_series")
	}
	if (frm.doc.voucher_type == "Journal Entry") {
	    frm.doc.naming_series = frappe.db.get_value("Branch",frm.doc.selco_branch,"selco_journal_entry_naming_series")
	}
	if (frm.doc.voucher_type == "Write Off Entry") {
	    frm.doc.naming_series = frappe.db.get_value("Branch",frm.doc.selco_branch,"selco_write_off_naming_series")
	}
	if (frm.doc.voucher_type == "Bank Payment") {
	    frm.doc.naming_series = frappe.db.get_value("Branch",frm.doc.selco_branch,"selco_bank_payment_naming_series")
	}
	if (frm.doc.voucher_type == "Receipt") {
	    frm.doc.naming_series = frappe.db.get_value("Branch",frm.doc.selco_branch,"selco_receipt_naming_series")
	}
	if (frm.doc.voucher_type == "Commission Journal") {
	    frm.doc.naming_series = frappe.db.get_value("Branch",frm.doc.selco_branch,"selco_commission_journal_naming_series")
	}
});

