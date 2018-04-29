cur_frm.add_fetch("supplier", "selco_gstin", "selco_supplier_gstin"); 
cur_frm.add_fetch("supplier", "selco_terms_and_conditions", "tc_name");



frappe.ui.form.on("Purchase Order", "refresh",
    function(frm) {
if ( cur_frm.doc.workflow_state == "AGM Approval Pending - PO" || cur_frm.doc.workflow_state == "Logistics Manager Approval Pending - PO" || cur_frm.doc.workflow_state == "Accounts Approval Pending - PO")
{
cur_frm.fields.forEach(function(l){ cur_frm.set_df_property(l.df.fieldname, "read_only", 1); })
var df = frappe.meta.get_docfield("Purchase Order Item", "item_code", cur_frm.doc.name);
df.read_only = 1;
var df = frappe.meta.get_docfield("Purchase Order Item", "item_name", cur_frm.doc.name);
df.read_only = 1;
var df = frappe.meta.get_docfield("Purchase Order Item", "schedule_date", cur_frm.doc.name);
df.read_only = 1;
var df = frappe.meta.get_docfield("Purchase Order Item", "expected_delivery_date", cur_frm.doc.name);
df.read_only = 1;
var df = frappe.meta.get_docfield("Purchase Order Item", "description", cur_frm.doc.name);
df.read_only = 1;
var df = frappe.meta.get_docfield("Purchase Order Item", "qty", cur_frm.doc.name);
df.read_only = 1;
var df = frappe.meta.get_docfield("Purchase Order Item", "uom", cur_frm.doc.name);
df.read_only = 1;
var df = frappe.meta.get_docfield("Purchase Order Item", "conversion_factor", cur_frm.doc.name);
df.read_only = 1;
var df = frappe.meta.get_docfield("Purchase Order Item", "price_list_rate", cur_frm.doc.name);
df.read_only = 1;
var df = frappe.meta.get_docfield("Purchase Order Item", "discount_percentage", cur_frm.doc.name);
df.read_only = 1;
var df = frappe.meta.get_docfield("Purchase Order Item", "rate", cur_frm.doc.name);
df.read_only = 1;
}
})

frappe.ui.form.on("Purchase Order", "refresh", function(frm) {
    cur_frm.set_query("selco_godown", function() {
        return {
            "filters": {
                "selco_type": "Godown"
            }
        };
    });
});

frappe.ui.form.on("Purchase Order Item","item_code",function(frm,cdt,cdn){
var d = locals[cdt][cdn];
d.warehouse = cur_frm.doc.selco_godown;
frm.set_df_property("selco_godown", "read_only",1);
});

frappe.ui.form.on("Purchase Order", "selco_godown", function(frm) {
	if (!frm.doc.selco_godown) { return 0; }
	frappe.call({
		method: "selco.selco.selco_customizations.get_default_address_name_and_display",
		args: {
			"doctype": "Warehouse",
			"docname": cur_frm.doc.selco_godown
		}
	}).done(function(r){
		frm.set_value("selco_godown_address", r.message.address_name);
		frm.set_value("selco_godown_address_details", r.message.address_display)
	}).error(function(err) {
		frappe.show_alert(err);
	});
});