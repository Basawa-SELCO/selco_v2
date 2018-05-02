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
});

