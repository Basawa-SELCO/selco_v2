cur_frm.add_fetch("selco_sales_account","selco_sales_tax_template","taxes_and_charges");

frappe.ui.form.on("Sales Invoice", "selco_type_of_invoice",
    function(frm) { console.log('tt');
if ( cur_frm.doc.selco_type_of_invoice == "System Sales Invoice" )
{
cur_frm.set_df_property("selco_service_bill_no", "reqd", true);
} else if( cur_frm.doc.selco_type_of_invoice == "Spare Sales Invoice" )
{
cur_frm.set_df_property("selco_service_bill_no", "reqd", false);
}
else if (cur_frm.doc.selco_type_of_invoice == "Service Bill")
{
cur_frm.set_df_property("selco_service_bill_no", "reqd", false);
}
});

frappe.ui.form.on("Sales Invoice", "refresh", function(frm) {
    cur_frm.set_query("selco_service_bill_no", function() {
        return {
            "filters": {
                "customer": frm.doc.customer,
                "selco_type_of_invoice": "Service Bill",
                "docstatus":1
            }
        };
    });
});


frappe.ui.form.on("Sales Invoice", "selco_type_of_invoice", function(frm) {

if ( cur_frm.doc.selco_type_of_invoice == "Service Bill") 	{
	cur_frm.fields_dict['items'].grid.get_field('item_code').get_query = function(doc) {
	return {
		filters: [
	            ['item_group', 'in', 'Installation Charges,AMC,Service Charges']	
			]
		}
	}
	refresh_field("items");
} else {
	cur_frm.fields_dict['items'].grid.get_field('item_code').get_query = function(doc) {
		return {
			filters: [
	            ['item_group', 'not in', 'Installation Charges,AMC,Service Charges']
			]
		}
	}
	refresh_field("items");
}
});



frappe.ui.form.on("Sales Invoice", "selco_type_of_invoice", function(frm) {
    if (cur_frm.doc.selco_type_of_invoice == "Service Bill") {
        cur_frm.set_query("selco_sales_account", function() {
            return {
                "filters": {
                    "parent_account": ["in", ["Karnataka Service - SELCO", "Tamilnadu Service - SELCO", "Interstate Service - SELCO"]]
                }
            };
        });
    }

 else if ((cur_frm.doc.selco_type_of_invoice == "System Sales Invoice") || (cur_frm.doc.selco_type_of_invoice == "Spare Sales Invoice"))
{
        cur_frm.set_query("selco_sales_account", function() {
            return {
                "filters": {
                    "parent_account": ["in", ["Karnataka Sales - SELCO"]]
                }
            };
        });
    }
    
else if(cur_frm.doc.selco_type_of_invoice == "Bill of Sale")
{
        cur_frm.set_query("selco_sales_account", function() {
            return {
                "filters": {
                    "parent_account": ["in", ["Interstate Sales - SELCO"]]
                }
            };
        });
    }
 

else if ((cur_frm.doc.selco_type_of_invoice == "System Sales Invoice") || (cur_frm.doc.selco_type_of_invoice == "Spare Sales Invoice")) {
    cur_frm.set_query("selco_sales_account", function() {
        return {
            "filters": {
                "parent_account": ["in", ["Karnataka Sales - SELCO"]]
            }
        };
    });
}

});
frappe.ui.form.on("Sales Invoice", "validate", function(frm) {
for (i=0;i<cur_frm.doc.taxes.length;i++)
{
if (cur_frm.doc.taxes[i].account_head == "Discount Karnataka 14.5% - SELCO")
{
//frappe.msgprint("Discount!!");
if(cur_frm.doc.taxes[i].tax_amount>0)
{
cur_frm.doc.taxes[i].tax_amount = cur_frm.doc.taxes[i].tax_amount * -1;
}
}
}
});










frappe.ui.form.on("Sales Invoice", "refresh", function(frm) {
if (frm.doc.__islocal)
{
if (cur_frm.doc.is_return == 1)
{
frm.set_value("selco_service_bill_no", "");
frm.refresh_field("selco_service_bill_no");
}
}
})


frappe.ui.form.on("Sales Invoice", "refresh", function(frm) {
cur_frm.fields_dict.customer.new_doc = quick_entry_customer;
cur_frm.fields_dict.customer_address.new_doc = quick_entry_address;
})


var quick_entry_address = function(){
console.log("Overrided");
	frappe._from_link = this;
	quick_entry("Address", 
	function(){}, 
	{ 
		"address_type": "Billing",
                "selco_branch": cur_frm.doc.selco_branch,
                "customer": cur_frm.doc.customer,
                "country" : "India"
	});
}

var quick_entry_customer = function(){
console.log("Overrided");
	frappe._from_link = this;
	quick_entry("Customer", 
	function(){}, 
	{ 
                "selco_branch": cur_frm.doc.selco_branch
	});
}

frappe.ui.form.on("Sales Invoice", "refresh", function(frm) {
if (cur_frm.doc.__islocal == 1)
{
if (frappe.user_info().email == "bangalore_service_center@selco-india.com")
{
cur_frm.doc.selco_branch = "Bangalore Service Branch";
cur_frm.set_df_property("branch", "read_only", true);
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
})

frappe.ui.form.on("Sales Invoice", "refresh", function (frm, cdt, cdn) {
  cur_frm.set_query("customer", function () {
    return { 
      query: "erpnext.controllers.queries.customer_query",
      searchfield: "selco_customer_contact_number"
    }
  });
});

quick_entry = function(doctype, success, fields_map={}) {
	frappe.model.with_doctype(doctype, function() {
		var mandatory = [];

		if (!fields_map == {}) {
			$.each(fields_map, function(k,v) {
				doc_field = frappe.meta.get_docfield(doctype, k)
				mandatory.push(doc_field);
			});
		} else {
			mandatory = $.map(frappe.get_meta(doctype).fields,
			function(d) { return (d.reqd || d.bold && !d.read_only) ? d : null });
		}

		var meta = frappe.get_meta(doctype);
		var doc = frappe.model.get_new_doc(doctype, null, null, true);

		/*if(meta.quick_entry != 1) {
			var d = frappe.model.make_new_doc_and_get_name(doctype);
			d = locals[doctype][d];
			$.each(fields_map, function(fieldname, fieldvalue) {
				d[fieldname] = fieldvalue;
			});
			frappe.set_route('Form', doctype, d.name);
			return;
		}*/

		var dialog = new frappe.ui.Dialog({
			title: __("New {0}", [doctype]),
			fields: mandatory,
		});

		var update_doc = function() {
			var data = dialog.get_values(true);
			$.each(data, function(key, value) {
				if(key==='__name') {
					dialog.doc.name = value;
				} else {
					if(!is_null(value)) {
						dialog.doc[key] = value;
					}
				}
			});
			return dialog.doc;
		}

		var open_doc = function() {
			dialog.hide();
			update_doc();
			frappe.set_route('Form', doctype, doc.name);
		}

		dialog.doc = doc;

		// refresh dependencies etc
		dialog.refresh();

		dialog.set_primary_action(__('Save'), function() {
			if(dialog.working) return;
			var data = dialog.get_values();

			if(data) {
				dialog.working = true;
				values = update_doc();
				frappe.call({
					method: "frappe.client.insert",
					args: {
						doc: values
					},
					callback: function(r) {
						dialog.hide();
						// delete the old doc
						frappe.model.clear_doc(dialog.doc.doctype, dialog.doc.name);
						var doc = r.message;
						if(success) {
							success(doc);
						}
						frappe.ui.form.update_calling_link(doc.name);
					},
					error: function() {
						open_doc();
					},
					always: function() {
						dialog.working = false;
					},
					freeze: true
				});
			}
		});

		var $link = $('<div class="text-muted small" style="padding-left: 10px; padding-top: 15px;">\
			Ctrl+enter to save | <a class="edit-full">Edit in full page</a></div>').appendTo(dialog.body);

		$link.find('.edit-full').on('click', function() {
			// edit in form
			open_doc();
		});

		// ctrl+enter to save
		dialog.wrapper.keydown(function(e) {
			if((e.ctrlKey || e.metaKey) && e.which==13) {
				if(!frappe.request.ajax_count) {
					// not already working -- double entry
					dialog.get_primary_btn().trigger("click");
				}
			}
		});

		dialog.show();

		//Set value and visibility if field map exists.
		if (fields_map != {}) {
			$.each(dialog.fields_dict, function(fieldname, field) {
				field.set_input(fields_map[fieldname]);
			});
		} else {
			// set defaults
			$.each(dialog.fields_dict, function(fieldname, field) {
				field.doctype = doc.doctype;
				field.docname = doc.name;
				if(!is_null(doc[fieldname])) {
					field.set_input(doc[fieldname]);
				}
			});
		}
	});
}
