/*To set naming series when branch is choosen for the first time */
cur_frm.add_fetch("selco_service_area", "selco_cse_service_area", "selco_service_area_name");


/*To set Branch eMail ID when branch is choosen for the first time */
cur_frm.add_fetch("selco_branch", "selco_branch_email_id", "selco_branch_email_id");
cur_frm.add_fetch("selco_branch", "selco_service_branch_email_id", "selco_service_branch_email_id");
cur_frm.add_fetch("selco_branch", "selco_customer_complaint_naming_series", "naming_series");

cur_frm.add_fetch("selco_customer_id", "selco_customer_contact_number", "selco_customer_contact_number");
cur_frm.add_fetch("selco_customer_id", "customer_name", "selco_customer_full_name");



cur_frm.add_fetch("selco_customer_id","selco_landline_mobile_2","selco_customer_contact_number_landline");
cur_frm.add_fetch("selco_complaint_handled_by", "service_person_name", "selco_service_person_name");

/*To 'Make Fields Read Only' once the workflow state changes to anything other than 'Complaint Drafted'*/
frappe.ui.form.on("Issue", "refresh",
    function(frm) {
if ( cur_frm.doc.workflow_state == "Complaint Open" || cur_frm.doc.workflow_state == "Complaint Assigned To CSE" || cur_frm.doc.workflow_state == "Complaint Cancelled" || cur_frm.doc.workflow_state == "Complaint Attended By CSE - Still Open" || cur_frm.doc.workflow_state == "Complaint Escalated To SBM" || cur_frm.doc.workflow_state == "Complaint Closed By Branch" || cur_frm.doc.workflow_state == "Complaint Closed By CSD" || cur_frm.doc.workflow_state == "Warranty Claim Format Raised - WC" || cur_frm.doc.workflow_state == "Dispatch Pending From Godown" || cur_frm.doc.workflow_state == "Dispatched From Godown")
{
frm.set_df_property("selco_complaint_received_date", "read_only",1);
frm.set_df_property("selco_branch", "read_only",1);
frm.set_df_property("subject", "read_only",1);
frm.set_df_property("selco_description_of_complaint", "read_only",1);
frm.set_df_property("selco_customer_id", "read_only",1);
frm.set_df_property("selco_customer_full_name", "read_only",1);

frm.set_df_property("selco_customer_contact_number", "read_only",1); frm.set_df_property("selco_customer_address", "read_only",1);
frm.set_df_property("selco_complaint_priority", "read_only",1);
frm.set_df_property("selco_warranty_applicable", "read_only",1);
frm.set_df_property("selco_type_of_system", "read_only",1);
frm.set_df_property("selco_capacity", "read_only",1);
frm.set_df_property("selco_warranty_claim_number", "read_only",1);
}
});

/*To 'Make Fields Read Only' once the workflow state changes to 'closed by branch' or 'closed by CSD'*/
frappe.ui.form.on("Issue", "refresh",
    function(frm) {
if ( cur_frm.doc.workflow_state == "Complaint Closed By CSD" || cur_frm.doc.workflow_state == "Complaint Closed By Branch" || cur_frm.doc.workflow_state == "Dispatch Pending From Godown")
{
frm.set_df_property("selco_ics_number", "read_only",1);
frm.set_df_property("selco_category_of_complaint", "read_only",1);
frm.set_df_property("selco_faulty_complaint", "read_only",1);
frm.set_df_property("selco_service_record_number", "read_only",1);
frm.set_df_property("selco_branch_remarks", "read_only",1);
frm.set_df_property("selco_sbm_name_if_involved", "read_only",1);
frm.set_df_property("selco_component_charges", "read_only",1);

frm.set_df_property("selco_ics_date", "read_only",1);
frm.set_df_property("selco_complaint_handled_by", "read_only",1);
frm.set_df_property("selco_faulty_component_vendor", "read_only",1);
frm.set_df_property("selco_record_date", "read_only",1);
frm.set_df_property("selco_service_charges_collected", "read_only",1);
frm.set_df_property("selco_sbm_remarks", "read_only",1);
}
})

frappe.ui.form.on("Issue", "selco_customer_id", function(frm) {
    frappe.call({
	    method: "frappe.contacts.doctype.address.address.get_default_address",
	    args: {
			doctype:"Customer",
			name: frm.doc.selco_customer_id
		}
	}).done(function(r){
		if(r.message) {
       		frm.set_value("selco_customer_address", r.message);
        }
	}).error(function(err){
		frappe.show_alert(__("Unable to load default address."));
	});
});


frappe.ui.form.on("Issue", "selco_customer_address", function(frm, cdt, cdn) {
	frappe.call({
		method: "frappe.contacts.doctype.address.address.get_address_display",
        args: {
            "address_dict": frm.doc.selco_customer_address
        },
	}).done(function(r){
		if(r.message) {
       		frm.set_value("selco_detail_address", r.message);
        }
	}).error(function(err){
		frappe.show_alert(__("Unable to load address display."));
	});
});


frappe.ui.form.on("Issue", "refresh", function (frm, cdt, cdn) {
  cur_frm.set_query("selco_customer_id", function () {
    return {
      query: "erpnext.controllers.queries.customer_query",
      searchfield: "selco_customer_contact_number"
    }
  });
});

frappe.ui.form.on("Issue", "refresh",
    function(frm) {
if ( cur_frm.doc.workflow_state == "Complaint Closed By CSD" || cur_frm.doc.workflow_state == "Complaint Rejected By CSD" )
{
frm.set_df_property("selco_remarks", "read_only",1);
frm.set_df_property("selco_special_budget", "read_only",1);
}
})


frappe.ui.form.on("Issue", "validate", function(frm, cdt, cdn) {
cur_frm.doc.selco_sms_number = cur_frm.doc.selco_customer_contact_number + "@sms.textlocal.in";console.log(cur_frm.doc.selco_sms_number);
})

frappe.ui.form.on("Issue", "validate",
    function(frm) {
if ( cur_frm.doc.workflow_state == "Complaint Closed By Branch" )
{
cur_frm.doc.selco_sms_counter_1 = cur_frm.doc.selco_sms_counter_1 +1 ;
}
})




frappe.ui.form.on("Issue", "refresh", function(frm) {
   {
var workflow_states = ['Complaint Open','Complaint Assigned To CSE','Complaint Escalated To SBM']
if (workflow_states.indexOf(cur_frm.doc.workflow_state) != -1)
{
      cur_frm.add_custom_button(__("Raise Warranty Claim"),
        cur_frm.cscript.raise_Warranty_Claim);
    }
}
})

cur_frm.cscript.raise_Warranty_Claim = function()
{
frappe.route_options = {
"selco_complaint_number": cur_frm.doc.name
};
frappe.new_doc("Warranty Claim");
}

frappe.ui.form.on("Issue", "refresh", function(frm) {
cur_frm.fields_dict.selco_customer_id.new_doc = quick_entry_customer;
//cur_frm.fields_dict.selco_customer_address.new_doc = quick_entry_address;
})
quick_entry_address = function(){
console.log("Overrided");
    frappe._from_link = this;
    quick_entry("Address",
    function(){},
    {
        "address_type": "Billing",
                "selco_branch": cur_frm.doc.selco_branch,
                "selco_customer_id": cur_frm.doc.selco_customer_id,
                "country" : "India",
                
    });
}

quick_entry_customer = function(){
    frappe._from_link = this;
    frappe.db.get_value("Branch", cur_frm.doc.selco_branch, "selco_customer_naming_series", function(r) {
    	quick_entry("Customer",
	    function(){},
		    {
		        "selco_branch": cur_frm.doc.selco_branch,
		        "naming_series": r.selco_customer_naming_series 
		    }
	    );
    });
}


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
