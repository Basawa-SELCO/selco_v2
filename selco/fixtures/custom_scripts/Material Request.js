/*To set naming series when branch is choosen for the first time */

cur_frm.add_fetch("selco_branch", "selco_branch_credit_limit", "selco_branch_credit_limit"); 
cur_frm.add_fetch("selco_branch", "selco_senior_sales_manager_email_id", "selco_senior_sales_manager_email_id"); 
cur_frm.add_fetch("selco_branch", "selco_godown_email_id", "selco_godown_email_id");
cur_frm.add_fetch("selco_branch", "selco_agm_email_id", "selco_agms_email_id"); 


frappe.ui.form.on("Material Request", "onload_post_render", function(frm) {
	cur_frm.remove_custom_button("Get Items from BOM");
});

frappe.ui.form.on("Material Request", "refresh", function(frm) {

	cur_frm.set_value("material_request_type","Material Transfer");

	 
    if (!cur_frm.custom_buttons[__("Get Items from BOM SELCO")]) {
      cur_frm.add_custom_button(__("Get Items from BOM SELCO"),
        cur_frm.cscript.get_items_from_bom1);
    }
    frm.remove_custom_button("Get Items from BOM");

    cur_frm.fields_dict['items'].grid.get_field('item_code').get_query = function(doc) {
	return {
	          "filters": {
	          "is_stock_item": "1"
	          }
		}
	}

	if (["Approval Pending by SM - IBM","Approval Pending by AGM - IBM","Approved - IBM","Partially Dispatched From Godown - IBM","Dispatched From Godown - IBM"].indexOf(cur_frm.doc.workflow_state) > -1)
	{
		cur_frm.fields.forEach(function(l){ cur_frm.set_df_property(l.df.fieldname, "read_only", 1); })
		frm.set_df_property("selco_dc_number", "read_only",0);
		frm.set_df_property("selco_dc_date", "read_only",0);
		frm.set_df_property("selco_godown_oa_comments", "read_only",0);

		var df = frappe.meta.get_docfield("Material Request Item", "item_code", cur_frm.doc.name);
		df.read_only = 1;
		var df = frappe.meta.get_docfield("Material Request Item", "item_name", cur_frm.doc.name);
		df.read_only = 1;
		var df = frappe.meta.get_docfield("Material Request Item", "selco_rate", cur_frm.doc.name);
		df.read_only = 1;
		var df = frappe.meta.get_docfield("Material Request Item", "qty", cur_frm.doc.name);
		df.read_only = 1;
		var df = frappe.meta.get_docfield("Material Request Item", "warehouse", cur_frm.doc.name);
		df.read_only = 1;
		var df = frappe.meta.get_docfield("Material Request Item", "description", cur_frm.doc.name);
		df.read_only = 1;
	}
	cur_frm.fields_dict['items'].grid.get_field('warehouse').get_query = function(doc) {
		return {
	          "filters": {
	          "type": "Virtual"
	          }
		}
	}

	set_branch_readonly(frm);


})


frappe.ui.form.on("Material Request", "validate", function(frm) {
	cur_frm.doc.selco_total_of_stock_and_debtors = cur_frm.doc.selco_present_debtors+cur_frm.doc.selco_stock_value
	cur_frm.doc.selco_present_limit = cur_frm.doc.selco_branch_credit_limit-cur_frm.doc.selco_total_of_stock_and_debtors

	cur_frm.clear_table("selco_items_print");
	cur_frm.refresh()
	var flag=0;

	var newrow = frappe.model.add_child(cur_frm.doc,"Material Request Item Print", "selco_items_print");
	if (cur_frm.doc.items.length)
	{
	newrow.item_code = cur_frm.doc.items[0].item_code
	newrow.item_name = cur_frm.doc.items[0].item_name
	newrow.quantity = cur_frm.doc.items[0].qty
	}

	for (var i = 1; i < cur_frm.doc.items.length; i++) { 
	for (var j = 0; j < cur_frm.doc.selco_items_print.length; j++) { 
	if (cur_frm.doc.items[i].item_code == cur_frm.doc.selco_items_print[j].item_code && cur_frm.doc.items[i].item_name == cur_frm.doc.selco_items_print[j].item_name)
	{
	flag = 1;
	cur_frm.doc.selco_items_print[j].quantity = cur_frm.doc.selco_items_print[j].quantity +cur_frm.doc.items[i].qty;
	refresh_field("selco_items_print");
	}
	}
	if(flag != 1)
	{
	var newrow = frappe.model.add_child(cur_frm.doc,"Material Request Item Print", "selco_items_print");
	newrow.item_code = cur_frm.doc.items[i].item_code
	newrow.item_name = cur_frm.doc.items[i].item_name
	newrow.quantity = cur_frm.doc.items[i].qty
	}
	flag=0;
	}

	for (var j = 0; j < cur_frm.doc.items.length; j++) 
	{ 
	if (!cur_frm.doc.items[j].warehouse) 
	{
	cur_frm.doc.items[j].warehouse = cur_frm.doc.selco_default_warehouse;
	}
	}

	for (var j = 0; j < cur_frm.doc.items.length; j++) {
        if ((cur_frm.doc.items[j].item_code == "2009032") || (cur_frm.doc.items[j].item_code == "2009040")) {
            cur_frm.set_value('selco_is_it_eshala_ibm', "YES")
        } else {
            cur_frm.set_value('selco_is_it_eshala_ibm', " ")

        }

    }
});


cur_frm.cscript.get_items_from_bom1 = function()
{
//console.log("Clicked Button" + cur_frm.doc.items[0].item_code);
if (cur_frm.doc.items.length == 0 || ((cur_frm.doc.items.length > 0) && (!cur_frm.doc.items[0].item_code)))
{
console.log("Inside");
cur_frm.clear_table("items");
}

		var d = new frappe.ui.Dialog({
			title: __("Get Items from BOM"),
			fields: [
				{"fieldname":"bom", "fieldtype":"Link", "label":__("BOM"),
					options:"BOM", reqd: 1, get_query: function(){
						return {filters: { docstatus:1 }}
					}},
				{"fieldname":"warehouse", "fieldtype":"Link", "label":__("Warehouse"),
					options:"Warehouse", reqd: 1, label:"For Warehouse"},
//Start of code added by Basawaraj for quantity field in 'Get Items from BOM' screen
				{fieldname:"Quantity", "label":__("Quantity"), "fieldtype":"Int",reqd: 1},
//End of code added by Basawaraj for quantity field in 'Get Items from BOM' screen
				{"fieldname":"fetch_exploded", "fieldtype":"Check",
					"label":__("Fetch exploded BOM (including sub-assemblies)"), "default":1},
				{fieldname:"fetch", "label":__("Get Items from BOM"), "fieldtype":"Button"}
			]
		});
		d.get_input("fetch").on("click", function() {
			var values = d.get_values();
			if(!values) return;
			values["company"] = cur_frm.doc.company;
			frappe.call({
				method: "erpnext.manufacturing.doctype.bom.bom.get_bom_items",
				args: values,
				callback: function(r) {
					console.log("MR BOM ITEMS", r);
					$.each(r.message, function(i, item) {
						var d = frappe.model.add_child(cur_frm.doc, "Material Request Item", "items");
						d.item_code = item.item_code;
						d.description = item.description;
						d.warehouse = values.warehouse;
						d.uom = item.stock_uom;
//End of code added by Basawaraj for quantity field calculation
						d.qty = item.qty * values.Quantity;
//End of code added by Basawaraj for quantity field calculation
//						d.qty = item.qty;
						d.conversion_factor = 1;
					});
					d.hide();
					refresh_field("items");
				}
			});
		});
		d.show();
	}
function set_branch_readonly(frm) {
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
	cur_frm.doc.selco_branch = "Mysore Service Branch";
	cur_frm.set_df_property("selco_branch", "read_only", true);
	}
	}
}
