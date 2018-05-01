cur_frm.add_fetch("selco_complaint_number", "selco_customer_id", "customer");
cur_frm.add_fetch("selco_complaint_number", "selco_customer_full_name", "customer_full_name");
cur_frm.add_fetch("selco_complaint_number", "selco_branch", "selco_branch");

cur_frm.add_fetch("selco_complaint_number", "selco_ics_number", "selco_ics_number");
cur_frm.add_fetch("selco_complaint_number", "selco_ics_date", "selco_ics_date");

cur_frm.add_fetch("selco_item_code2", "item_name", "selco_item_name");
cur_frm.add_fetch("selco_item_code2", "item_group", "item_group");
cur_frm.add_fetch("selco_item_code2", "description", "item_description");

cur_frm.add_fetch("selco_panel_capacity", "item_name", "selco_panel_name");
cur_frm.add_fetch("selco_battery_capacity", "item_name", "selco_battery_name"); 
cur_frm.add_fetch("selco_inverter_capacity", "item_name", "selco_inverter_name"); 
cur_frm.add_fetch("selco_water_heater_capacity", "item_name", "selco_water_heater_name"); 


frappe.ui.form.on("Warranty Claim", "selco_panel", function(frm) {
cur_frm.set_query("selco_item_code2", function() {
    return {
        filters: [
            ['Item', 'item_group', 'in', 'Modules, Common Item']
        ]
    }
});

cur_frm.set_query("supplier", function() {
    return {
        filters: [
            ['Supplier', 'supplier_type', 'in', 'Module Manufacturer, Common Supplier']
        ]
    };
});

})


frappe.ui.form.on("Warranty Claim", "selco_battery", function(frm) {
cur_frm.set_query("selco_item_code2", function() {
    return {
        filters: [
            ['Item', 'item_group', 'in', 'Batteries, Common Item']
        ]
    }
});

cur_frm.set_query("supplier", function() {
    return {
        filters: [
            ['Supplier', 'supplier_type', 'in', 'Battery Manufacturer, Common Supplier']
        ]
    };
});

})



frappe.ui.form.on("Warranty Claim", "selco_inverter", function(frm) {
cur_frm.set_query("selco_item_code2", function() {
    return {
        filters: [
            ['Item', 'item_group', 'in', 'Inverters, Common Item']
        ]
    }
});

cur_frm.set_query("supplier", function() {
    return {
        filters: [
            ['Supplier', 'supplier_type', 'in', 'Inverter Manufacturer, Common Supplier']
        ]
    };
});

})



frappe.ui.form.on("Warranty Claim", "selco_water_heater", function(frm) {
cur_frm.set_query("selco_item_code2", function() {
    return {
        filters: [
            ['Item', 'item_group', 'in', 'ETC Water Heater Systems, Common Item ,Water Heater Consumables,Water Heater Tanks Spare']
        ]
    }
});

cur_frm.set_query("supplier", function() {
    return {
        filters: [
            ['Supplier', 'supplier_type', 'in', 'Solar Water Heater ETC Manufacturer, Common Supplier']
        ]
    };
});

})



frappe.ui.form.on("Warranty Claim", "validate", function(frm) {
        if ( cur_frm.doc.workflow_state=="Warranty Claim Format Raised - WC")
        {
        frappe.call({
            "method": "frappe.client.set_value",
            "args": {
                "doctype": "Issue",
                "name": frm.doc.selco_complaint_number,
                "fieldname": "workflow_state",
                "value": "Warranty Claim Format Raised - WC"
            }
        });
        }
});

frappe.ui.form.on("Warranty Claim", "validate", function(frm) {
        if ( cur_frm.doc.workflow_state=="Warranty Claim Approved - WC")
        {
        frappe.call({
            "method": "frappe.client.set_value",
            "args": {
                "doctype": "Issue",
                "name": frm.doc.selco_complaint_number,
                "fieldname": "workflow_state",
                "value": "Dispatch Pending From Godown"
            }
        });
        }
});

frappe.ui.form.on("Warranty Claim", "validate", function(frm) {
        if ( cur_frm.doc.workflow_state=="Warranty Claim Rejected - WC")
        {
        frappe.call({
            "method": "frappe.client.set_value",
            "args": {
                "doctype": "Issue",
                "name": frm.doc.selco_complaint_number,
                "fieldname": "workflow_state",
                "value": "Complaint Attended By CSE - Still Open"
            }
        });
        }
});


frappe.ui.form.on("Warranty Claim", "validate", function(frm) {
        if ( cur_frm.doc.workflow_state=="Dispatched From Godown")
        {
        frappe.call({
            "method": "frappe.client.set_value",
            "args": {
                "doctype": "Issue",
                "name": frm.doc.selco_complaint_number,
                "fieldname": "workflow_state",
                "value": "Dispatched From Godown"
            }
        });
        }
});


frappe.ui.form.on("Warranty Claim", "selco_branch", function(frm, cdt, cdn) {
	var d = locals[cdt][cdn];
	frappe.call({
		"method": "frappe.client.get",
		args: {
			doctype: "Branch",
			name: d.selco_branch
		},
		callback: function (data) {
			frappe.model.set_value(d.doctype, d.name, "godown_email_id", data.message.godown_email_id);

		}
	})
});

frappe.ui.form.on("Warranty Claim", "selco_branch", function(frm, cdt, cdn) {
	var d = locals[cdt][cdn];
	frappe.call({
		"method": "frappe.client.get",
		args: {
			doctype: "Branch",
			name: d.selco_branch
		},
		callback: function (data) {
			frappe.model.set_value(d.doctype, d.name, "senior_service_manager_email_id",data.message.senior_service_manager_email_id);

		}
	})
});


frappe.ui.form.on("Warranty Claim", "refresh",
    function(frm) {
if ( cur_frm.doc.workflow_state == "Warranty Claim Format Raised - WC" || cur_frm.doc.workflow_state == "Warranty Claim Approved - WC" || cur_frm.doc.workflow_state == "Warranty Claim Rejected - WC" || cur_frm.doc.workflow_state == "Dispatched From Godown")
{
cur_frm.fields.forEach(function(l){ cur_frm.set_df_property(l.df.fieldname, "read_only", 1); })
frm.set_df_property("selco_dc_number", "read_only",0);
frm.set_df_property("selco_remarks_by_godown", "read_only",0);
frm.set_df_property("selco_docket_number_and_details_branch_to_godown", "read_only",0);
frm.set_df_property("selco_docket_number_and_details_godown_to_branch", "read_only",0);
frm.set_df_property("selco_docket_date_branch_to_godown", "read_only",0);
frm.set_df_property("selco_docket_date_godown_to_branch", "read_only",0);



//frm.set_df_property("selco_item_code2", "read_only",0);
//frm.set_df_property("selco_item_name", "read_only",0);
//frm.set_df_property("item_serial_number", "read_only",0);
//frm.set_df_property("supplier", "read_only",0);
//frm.set_df_property("within_warranty", "read_only",0);
}
})




