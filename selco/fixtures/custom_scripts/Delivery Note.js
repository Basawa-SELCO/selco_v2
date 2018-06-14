/*To set naming series when branch is choosen for the first time */
cur_frm.add_fetch("selco_branch", "selco_delivery_note_naming_series", "naming_series"); 

/*To set naming series when the value in branch is changed*/
frappe.ui.form.on("Delivery Note", "selco_branch", function(frm) {
  if (cur_frm.doc.naming_series == null )   {
    window.location.reload();
    msgprint("Please set the correct naming series for the branch.");
           throw "Not allowed";
  }
});

frappe.ui.form.on("Delivery Note", "refresh", function(frm) {
   if (frm.doc.docstatus == 0){
      cur_frm.add_custom_button(__("Get Items from BOM"),
      cur_frm.cscript.get_items_from_bom2);
    }
});

cur_frm.cscript.get_items_from_bom2 = function() {

if (cur_frm.doc.items.length > 0 && !cur_frm.doc.items[0].item_code) {
  cur_frm.clear_table("items");
}

  var d = new frappe.ui.Dialog({
    title: __("Get Items from BOM"),
    fields: [
      {"fieldname":"bom", "fieldtype":"Link", "label":__("BOM"),
        options:"Stock Entry", reqd: 1, get_query: function(){
          return {filters: { purpose:"Repack", docstatus: 1}}
        }},
      {fieldname:"fetch", "label":__("Get Items from BOM"), "fieldtype":"Button"}
    ]
  });
  d.get_input("fetch").on("click", function() {
    var values = d.get_values();
    cur_frm.doc.imported_system = values.bom;
    if(!values) return;
    frappe.call({
      "method": "frappe.client.get",
      args: {
        doctype: "Stock Entry",
        name:values.bom
      },
      callback: function (data) {
        console.log(data);
        if (data.message) {
        for (i=0;i<data.message.items.length;i++)
        {
          if (data.message.items[i].t_warehouse)
          {
        var newrow = frappe.model.add_child(cur_frm.doc,"Delivery Note Item", "items");
        newrow.item_code=data.message.items[i].item_code;
        newrow.item_name=data.message.items[i].item_name;
        newrow.qty=data.message.items[i].qty;
        newrow.stock_uom=data.message.items[i].stock_uom;
        newrow.uom=data.message.items[i].uom;
        newrow.description=data.message.items[i].description;
        newrow.rate=data.message.items[i].basic_rate//11000;
        newrow.amount=data.message.items[i].amount
      }
        //console.log(data.message.items[i]);
        }

        }
        refresh_field("items");
        d.hide();
    }
    })

  });
  d.show();
}