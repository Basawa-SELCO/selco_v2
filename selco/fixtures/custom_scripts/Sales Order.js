/*To set naming series when branch is choosen for the first time */
cur_frm.add_fetch("selco_branch", "sales_order_naming_series", "naming_series"); 

/*To set naming series when the value in branch is changed*/
frappe.ui.form.on("Sales Order", "selco_branch",
    function(frm) {
cur_frm.add_fetch("selco_branch", "sales_order_naming_series", "naming_series");

if ( cur_frm.doc.naming_series == null )
{
window.location.reload();
msgprint("Please set the correct naming series for the branch.");
       throw "Not allowed";
}
})