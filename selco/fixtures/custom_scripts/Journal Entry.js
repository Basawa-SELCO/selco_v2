/*To set naming series when branch is choosen for the first time */
cur_frm.add_fetch("selco_branch", "selco_receipt_naming_series", "naming_series"); 

/*To set naming series when the value in branch is changed
frappe.ui.form.on("Journal Entry", "selco_branch",
    function(frm) {
cur_frm.add_fetch("selco_branch", "receipt_naming_series", "naming_series");

if ( cur_frm.doc.naming_series == null )
{
window.location.reload();
msgprint("Please set the correct naming series for the branch.");
       throw "Not allowed";
}
})*/
frappe.ui.form.on("Journal Entry", "validate", function(frm) {
if (user_roles.indexOf("SELCO Lead Accountant")!=-1 && cur_frm.doc.voucher_type=="Write Off Entry")
 frappe.throw("You are not allowed to raise the journal entry of type write off!!");
})


frappe.ui.form.on("Journal Entry", "refresh", function(frm) {
{
if(!cur_frm.doc.__islocal)
//frappe.model.add_child(cur_frm.doc, "Journal Entry Account", 'accounts')
//refresh_field("accounts");
cur_frm.set_df_property("voucher_type", "read_only", true);
}
})

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
})


frappe.ui.form.on("Journal Entry", "refresh", function(frm) {
if (cur_frm.doc.__islocal == 1)
{
if (frappe.user_info().email == "bangalore_service_center@selco-india.com")
{
cur_frm.doc.selco_branch = "Bangalore Service Branch";
cur_frm.set_df_property("selco_branch", "read_only", true);
} else if (frappe.user_info().email == "kundapura_service_center@selco-india.com")
{
cur_frm.doc.selco_branch = "Kundapur Service Branch";
cur_frm.set_df_property("selco_branch", "read_only", true);
}else if (frappe.user_info().email == "puttur_service_center@selco-india.com")
{
cur_frm.doc.selco_branch = "Puttur Service Branch";
cur_frm.set_df_property("selco_branch", "read_only", true);
}else if (frappe.user_info().email == "hassan_service_center@selco-india.com")
{
cur_frm.doc.selco_branch = "Hassan Service Branch";
cur_frm.set_df_property("selco_branch", "read_only", true);
}else if (frappe.user_info().email == "bellary_service_center@selco-india.com")
{
cur_frm.doc.selco_branch = "Ballari Service Branch";
cur_frm.set_df_property("selco_branch", "read_only", true);
}else if (frappe.user_info().email == "shimoga_service_center@selco-india.com")
{
cur_frm.doc.selco_branch = "Shivamogga Service Branch";
cur_frm.set_df_property("selco_branch", "read_only", true);
}else if (frappe.user_info().email == "chitradurga_service_center@selco-india.com")
{
cur_frm.doc.selco_branch = "Chitradurga Service Branch";
cur_frm.set_df_property("selco_branch", "read_only", true);
}else if (frappe.user_info().email == "dharwad_service_center@selco-india.com")
{
cur_frm.doc.selco_branch = "Dharwad Service Branch";
cur_frm.set_df_property("selco_branch", "read_only", true);
}else if (frappe.user_info().email == "vijayapura_service_center@selco-india.com")
{
cur_frm.doc.selco_branch = "Vijayapura Service Branch";
cur_frm.set_df_property("selco_branch", "read_only", true);
}else if (frappe.user_info().email == "mysore_service_center@selco-india.com")
{
cur_frm.doc.branch = "Mysore Service Branch";
cur_frm.set_df_property("selco_branch", "read_only", true);
}
}
})

frappe.ui.form.on("Journal Entry", "voucher_type", function(frm, cdt, cdn) {
if(cur_frm.doc.voucher_type == "Commission Journal" && cur_frm.doc.selco_branch == "Head Office")
{
cur_frm.doc.naming_series = "CJ/HO/17-18/";
refresh_field("naming_series");
}
})


