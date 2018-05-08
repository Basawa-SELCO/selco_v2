cur_frm.add_fetch("selco_branch", "selco_branch_email_id", "selco_branch_email_id");


frappe.ui.form.on("Stock Entry", "selco_supplier_or_customer", function(frm) {
if ((cur_frm.doc.selco_supplier_or_customer == "Customer")
&& (cur_frm.doc.selco_type_of_stock_entry=="Rejection In"))
{
cur_frm.set_df_property("items", "read_only", false);
}
else if ((cur_frm.doc.selco_supplier_or_customer == "Customer")
&& (cur_frm.doc.selco_type_of_stock_entry=="Rejection Out"))
{
cur_frm.set_df_property("items", "read_only", true);
}
else if ((cur_frm.doc.selco_supplier_or_customer == "Supplier") && (cur_frm.doc.selco_type_of_stock_entry=="Rejection In"))
{
cur_frm.set_df_property("rejection_out_id", "reqd", true);
cur_frm.set_df_property("items", "read_only", true);
}
else if ((cur_frm.doc.selco_supplier_or_customer == "Supplier") && (cur_frm.doc.selco_type_of_stock_entry=="Rejection Out"))
{
cur_frm.set_df_property("items", "read_only", false);
}

})

  
frappe.ui.form.on('Stock Entry', 'selco_supplier_or_customer_id', function(frm, cdt, cdn) {
     var d = frappe.model.get_doc(cdt, cdn);
     frappe.call({
        method: "frappe.client.get_value",
args: {
doctype: d.selco_supplier_or_customer,
fieldname: d.selco_supplier_or_customer=='Customer' ? 'customer_name' : 'supplier_name',
filters: { name: d.selco_supplier_or_customer_id },
},
callback: function(r, rt) {
if(r.message) {
if (d.selco_supplier_or_customer == "Customer")
{
frappe.model.set_value(d.doctype, d.name, 'selco_supplier_or_customer_name', r.message.customer_name);
}
else if (d.selco_supplier_or_customer == "Supplier")
{
frappe.model.set_value(d.doctype, d.name, 'selco_supplier_or_customer_name', r.message.supplier_name);
}
console.log("callback executed!!");
}
}
    })
})


frappe.ui.form.on("Stock Entry", "selco_type_of_stock_entry", function(frm) {
cur_frm.set_df_property("selco_type_of_stock_entry", "read_only", true);
cur_frm.clear_table("items");
cur_frm.set_df_property("items", "read_only", true);
cur_frm.set_df_property("rejection_out_id", "reqd", false);

if (cur_frm.doc.selco_type_of_stock_entry == "GRN")
{
cur_frm.set_df_property("items", "read_only", true);
cur_frm.set_value('purpose', "Material Transfer")
cur_frm.set_value('selco_inward_or_outward', "Inward")
}
else if (cur_frm.doc.selco_type_of_stock_entry == "Outward DC")
{
cur_frm.set_value('purpose', "Material Transfer")
cur_frm.set_value('selco_inward_or_outward', "Outward")
cur_frm.set_df_property("selco_being_dispatched_to", "reqd", true);
}
else if (cur_frm.doc.selco_type_of_stock_entry == "BOM")
{
cur_frm.set_value('purpose', "Repack")
cur_frm.set_value('selco_inward_or_outward', "")
cur_frm.doc.selco_type_of_material = "Good Stock";
cur_frm.doc.selco_inward_or_outward = "";
cur_frm.set_df_property("selco_type_of_material", "read_only", true);
cur_frm.set_df_property("items", "read_only", false);

}
else if (cur_frm.doc.selco_type_of_stock_entry == "Rejection In")
{
cur_frm.set_value('purpose', "Material Receipt")
cur_frm.set_value('selco_inward_or_outward', "")
cur_frm.doc.selco_type_of_material = "Repair Stock";
cur_frm.set_df_property("selco_type_of_material", "read_only", true);
cur_frm.set_df_property("selco_supplier_or_customer", "reqd", true);
cur_frm.set_df_property("selco_supplier_or_customer_id", "reqd", true);
}
else if (cur_frm.doc.selco_type_of_stock_entry == "Rejection Out")
{
cur_frm.set_value('purpose', "Material Issue")
cur_frm.set_value('selco_inward_or_outward', "")
cur_frm.doc.selco_type_of_material = "Repair Stock";
cur_frm.set_df_property("selco_type_of_material", "read_only", true);
cur_frm.set_df_property("selco_supplier_or_customer", "reqd", true);
cur_frm.set_df_property("selco_supplier_or_customer_id", "reqd", true);
}

toggle_custom_buttons(frm);

});

 

frappe.ui.form.on("Stock Entry", "selco_inward_or_outward", function(frm, cdt, cdn) {
if (cur_frm.doc.selco_inward_or_outward == "Inward")
{
cur_frm.clear_table("items");
cur_frm.set_df_property("items", "read_only", true);
} else
{
cur_frm.set_df_property("items", "read_only", false);
}
})

frappe.ui.form.on("Stock Entry", "purpose", function(frm) {
if(cur_frm.doc.purpose=="Material Issue")
{

cur_frm.clear_table("items");
cur_frm.set_df_property("items", "read_only", true);

    cur_frm.set_query("selco_rejection_in_id", function() {
        return {
            "filters": {
                "supplier_or_customer_id": frm.doc.selco_supplier_or_customer_id,
                "purpose": "Material Receipt",
                "docstatus":1
            }
        };
    });
}
});

frappe.ui.form.on("Stock Entry", "purpose", function(frm, cdt, cdn) {
refresh_field("selco_type_of_material");
if (cur_frm.doc.purpose == "Repack")
{
cur_frm.doc.selco_type_of_material = "Good Stock";
cur_frm.doc.selco_inward_or_outward = "";
cur_frm.set_df_property("selco_type_of_material", "read_only", true);
} else if ( (cur_frm.doc.purpose == "Material Receipt"))
{
cur_frm.doc.selco_type_of_material = "Repair Stock";
cur_frm.set_df_property("selco_type_of_material", "read_only", true);
cur_frm.set_df_property("selco_supplier_or_customer", "reqd", true);
cur_frm.set_df_property("selco_supplier_or_customer_id", "reqd", true);
} else if(cur_frm.doc.purpose == "Material Issue")
{
cur_frm.doc.selco_type_of_material = "Repair Stock";
cur_frm.set_df_property("selco_type_of_material", "read_only", true);
cur_frm.set_df_property("selco_supplier_or_customer", "reqd", true);
cur_frm.set_df_property("selco_supplier_or_customer_id", "reqd", true);
} 
else if (cur_frm.doc.purpose == "Material Transfer")
{
cur_frm.set_df_property("selco_type_of_material", "read_only", false);
refresh_field("selco_type_of_material");
}
})

frappe.ui.form.on("Stock Entry", "to_warehouse", function(frm, cdt, cdn) {console.log('p');
  var d = locals[cdt][cdn];
  frappe.call({
    "method": "frappe.client.get",
    args: {
      doctype: "Warehouse",
      name: d.to_warehouse
    },
    callback: function (data) { console.log('p');
      frappe.model.set_value(d.doctype, d.name, "selco_recipient_address_link",data.message.address);

    }
  })
})

frappe.ui.form.on("Stock Entry", "selco_recipient_address_link", function(frm, cdt, cdn) {
  return frm.call({
      method: "frappe.contacts.doctype.address.address.get_address_display",
      args: {
          "address_dict": frm.doc.selco_recipient_address_link
      },
      callback: function(r) {
        if(r.message) {
         frappe.model.set_value(cdt,cdn,"selco_recipient_address", r.message);
        }
      }
  });
});


frappe.ui.form.on("Stock Entry", "refresh", function(frm) {
  cur_frm.set_query("selco_supplier_or_customer", function() {
    return {
      "filters": {
        "name":["in", ["Customer", "Supplier"]]
      }
    };
  });

  toggle_custom_buttons(frm);
});



frappe.ui.form.on("Stock Entry", "selco_get_items_from_supplier_reference", function(frm,cdt,cdn) {
console.log("Button Clicked");
cur_frm.set_df_property("items", "read_only", true);
      frappe.call({           "method":"selco.selco.selco_customizations.get_items_from_outward_stock_entry",
      args:{ selco_doc_num : cur_frm.doc.selco_suppliers_ref,selco_branch : cur_frm.doc.selco_branch},
        callback: function (data) {
cur_frm.doc.from_warehouse = data.message.from_warehouse;
cur_frm.doc.to_warehouse = data.message.to_warehouse;
cur_frm.clear_table("items");
for (i = 0; i < data.message.dc.items.length; i++) { 
var newrow = frappe.model.add_child(cur_frm.doc,"Stock Entry Detail", "items");
newrow.item_code = data.message.dc.items[i].item_code;
newrow.item_name = data.message.dc.items[i].item_name;
newrow.qty = data.message.dc.items[i].qty;
newrow.uom = data.message.dc.items[i].uom;
newrow.transfer_qty = data.message.dc.items[i].transfer_qty;
newrow.conversion_factor = data.message.dc.items[i].conversion_factor;
refresh_field("items");
refresh_field("from_warehouse");
refresh_field("to_warehouse");

}
}
})
});



frappe.ui.form.on("Stock Entry", "selco_get_items_from_rejection_in", function(frm,cdt,cdn) {
console.log("Button Clicked");
cur_frm.set_df_property("items", "read_only", true);
      frappe.call({           "method":"selco.selco.selco.selco_customizations.selco_get_items_from_rejection_in",
        args:{ selco_rej_in : cur_frm.doc.selco_rejection_in_id,selco_branch : cur_frm.doc.selco_branch},
        callback: function (data) { console.log(data);
cur_frm.doc.from_warehouse = data.message.from_warehouse;
cur_frm.clear_table("items");
for (i = 0; i < data.message.dc.items.length; i++) { 
var newrow = frappe.model.add_child(cur_frm.doc,"Stock Entry Detail", "items");
newrow.item_code = data.message.dc.items[i].item_code;
newrow.qty = data.message.dc.items[i].qty;
newrow.uom = data.message.dc.items[i].uom;
newrow.transfer_qty = data.message.dc.items[i].transfer_qty;
newrow.conversion_factor = data.message.dc.items[i].conversion_factor;
refresh_field("items");
refresh_field("from_warehouse");
refresh_field("to_warehouse");

}
}
})
});



// frappe.ui.form.on("Stock Entry", "refresh", function(frm) {
//    // {
//    //    cur_frm.add_custom_button(__("Get Items from IBM"),
//    //      cur_frm.cscript.get_items_from_ibm1);
//    //  }
   
// })

 cur_frm.cscript.get_items_from_ibm1 = function()
{
cur_frm.clear_table("items");
  var d = new frappe.ui.Dialog({
    title: __("Get Items from IBM"),
    fields: [
      {"fieldname":"ibm", "fieldtype":"Link", "label":__("IBM"),
        options:"Material Request", reqd: 1, get_query: function(){
          //return {filters: { workflow_state:"Approved - IBM",branch:cur_frm.doc.branch}}
          //return {filters: { workflow_state:["in", ["Approved - IBM", "Partially Dispatched From Godown - IBM"]] ,selco_branch:cur_frm.doc.selco_branch}}
          return {filters: {selco_branch:cur_frm.doc.selco_being_dispatched_to}}
        }},
      {fieldname:"fetch", "label":__("Get Items from IBM"), "fieldtype":"Button"}
    ]
  });
  d.get_input("fetch").on("click", function() {
    var values = d.get_values();
    console.log(values.ibm)
    if(!values) return;
    frappe.call({
      "method": "frappe.client.get",
      args: {
        doctype: "Material Request",
        name:values.ibm
      },
      callback: function (data) {
        if (data.message) {
        for (i=0;i<data.message.items.length;i++)
        {
        var newrow = frappe.model.add_child(cur_frm.doc,"Stock Entry Detail", "items");
        newrow.item_code=data.message.items[i].item_code;
        newrow.item_name=data.message.items[i].item_name;
        newrow.qty=data.message.items[i].qty;
        newrow.transfer_qty=data.message.items[i].qty;
        newrow.uom=data.message.items[i].uom;
        newrow.stock_uom=data.message.items[i].uom;
        newrow.conversion_factor=1;
        }
        }
        refresh_field("items");
        d.hide();
    }
    })

  });
  d.show();
}

frappe.ui.form.on("Stock Entry", "selco_supplier_or_customer", function(frm) {
    if (cur_frm.doc.selco_type_of_stock_entry == "Rejection In" && cur_frm.doc.selco_supplier_or_customer == "Supplier") {
        cur_frm.add_custom_button(__("Get Items From Rejection Out"), cur_frm.cscript.get_items_from_rejection_out);
    } else if (cur_frm.doc.selco_type_of_stock_entry == "Rejection Out" && cur_frm.doc.selco_supplier_or_customer == "Customer") {
        cur_frm.add_custom_button(__("Get Items From Rejection In"), cur_frm.cscript.get_items_from_rejection_in);
    }
});


cur_frm.cscript.get_items_from_rejection_in = function()
{
console.log("clicked on");

  var d = new frappe.ui.Dialog({
      title: __("Get Items from Rejection In"),
      fields: [{
              "fieldname": "rejection_in",
              "fieldtype": "Link",
              "label": __("Rejection In"),
              options: "Stock Entry",
              reqd: 1,
              get_query: function() {

                  return {
                      filters: {
                          selco_type_of_stock_entry: "Rejection In",selco_branch:cur_frm.doc.selco_branch,selco_supplier_or_customer_id:cur_frm.doc.selco_supplier_or_customer_id,docstatus:1
                      }
                  }
              }
          },
          {
              fieldname: "fetch",
              "label": __("Get Items from Rejection In"),
              "fieldtype": "Button"
          }
      ]
  });
  d.get_input("fetch").on("click", function() {
    var values = d.get_values();
    console.log(values.rejection_in)
    if(!values) return;
    frappe.call({
      "method": "frappe.client.get",
      args: {
        doctype: "Stock Entry",
        name:values.rejection_in
      },
      callback: function (data) {
        if (data.message) {
        for (i=0;i<data.message.items.length;i++)
        {
         console.log(data.message.items[i]);
         var newrow = frappe.model.add_child(cur_frm.doc,"Stock Entry Detail", "items");
newrow.item_code = data.message.items[i].item_code;
newrow.qty = data.message.items[i].qty - data.message.items[i].reference_rej_in_or_rej_quantity;
newrow.uom = data.message.items[i].uom;
newrow.transfer_qty = data.message.items[i].transfer_qty;
newrow.conversion_factor = data.message.items[i].conversion_factor;
newrow.reference_rej_in_or_rej_ot = data.message.name;

        }
        }
        refresh_field("items");
        d.hide();
    }
    })

  });
  d.show();


}

cur_frm.cscript.get_items_from_rejection_out = function()
{
console.log("clicked on rejection out");

  var d = new frappe.ui.Dialog({
      title: __("Get Items from Rejection Out"),
      fields: [{
              "fieldname": "rejection_out",
              "fieldtype": "Link",
              "label": __("Rejection Out"),
              options: "Stock Entry",
              reqd: 1,
              get_query: function() {

                  return {
                      filters: {
                          selco_type_of_stock_entry: "Rejection Out",selco_branch:cur_frm.doc.selco_branch,selco_supplier_or_customer_id:cur_frm.doc.selco_supplier_or_customer_id,docstatus:1
                      }
                  }
              }
          },
          {
              fieldname: "fetch",
              "label": __("Get Items from Rejection Out"),
              "fieldtype": "Button"
          }
      ]
  });
  d.get_input("fetch").on("click", function() {
    var values = d.get_values();
    console.log(values.rejection_out)
    if(!values) return;
    frappe.call({
      "method": "frappe.client.get",
      args: {
        doctype: "Stock Entry",
        name:values.rejection_out
      },
      callback: function (data) {
        if (data.message) {
        for (i=0;i<data.message.items.length;i++)
        {
         console.log(data.message.items[i]);
         var newrow = frappe.model.add_child(cur_frm.doc,"Stock Entry Detail", "items");
newrow.item_code = data.message.items[i].item_code;
newrow.qty = data.message.items[i].qty - data.message.items[i].reference_rej_in_or_rej_quantity;
newrow.uom = data.message.items[i].uom;
newrow.transfer_qty = data.message.items[i].transfer_qty;
newrow.conversion_factor = data.message.items[i].conversion_factor;
newrow.reference_rej_in_or_rej_ot = data.message.name;

        }
        }
        refresh_field("items");
        d.hide();
    }
    })

  });
  d.show();


}
frappe.ui.form.on("Stock Entry", "refresh", function(frm) {
if (cur_frm.doc.__islocal == 1)
{
if (frappe.user_info().email == "southgodown@selco-india.com")
{
cur_frm.doc.selco_branch = "Manipal Godown";
cur_frm.set_df_property("selco_branch", "read_only", true);
} else if (frappe.user_info().email == "northgodown@selco-india.com")
{
cur_frm.doc.selco_branch = "Dharwad Godown";
cur_frm.set_df_property("selco_branch", "read_only", true);
}else if (frappe.user_info().email == "bangalore_godown@selco-india.com")
{
cur_frm.doc.selco_branch = "Bangalore Godown";
cur_frm.set_df_property("selco_branch", "read_only", true);
}
}
})

frappe.ui.form.on("Stock Entry", "from_warehouse", function(frm) {
  get_warehouse_address(frm, frm.doc.from_warehouse, "source_warehouse_address");
});

frappe.ui.form.on("Stock Entry", "to_warehouse", function(frm) {
  get_warehouse_address(frm, frm.doc.to_warehouse, "target_warehouse_address");
});

function get_warehouse_address(frm, warehouse_name, field_to_set) {
  frappe.call({
    method: "selco.selco.selco_customizations.get_default_address_name_and_display",
    args: {
      "doctype": "Warehouse",
      "docname": warehouse_name
    } 
  }).done(function(r){
    console.log(r);
    if(r.message) {
      frm.set_value(field_to_set, r.message.address_name);
    }
  }).error(function(err) {
    frappe.show_alert("Unable to fetch address details");
    console.log(err);
  });
}

function update_warehouse_in_items(frm, source_or_target, warehouse_name) {
  frm.doc.items.forEach(function(item) {
    if (source_or_target == "Source" && item.s_warehouse === undefined) {
      item.s_warehouse = warehouse_name;
    } 
    if (source_or_target == "Target" && item.t_warehouse === undefined) {
      item.t_warehouse = warehouse_name;
    } 
  });
  refresh_field("items")
}


function toggle_custom_buttons(frm) {
    if (!in_list(["Rejection Out", "Rejection In"], frm.doc.selco_type_of_stock_entry)) {
      if (!frm.custom_buttons["Get Items from IBM"]) {
        frm.add_custom_button(__("Get Items from IBM"), cur_frm.cscript.get_items_from_ibm1);
      }
    } else {
      frm.remove_custom_button("Get Items from IBM");
      frm.remove_custom_button("Make Material Request");
      frm.remove_custom_button("Purchase Invoice", "Get items from");
    }  
}
