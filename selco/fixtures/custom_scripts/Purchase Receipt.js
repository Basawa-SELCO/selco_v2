cur_frm.add_fetch("selco_godown", "selco_mrn_naming_series", "naming_series");

frappe.ui.form.on("Purchase Receipt", "refresh", function(frm) {
console.log('hh');
    cur_frm.set_query("selco_godown", function() {
        return {
            "filters": {
                "selco_type": "Godown"
            }
        };
    });
});


frappe.ui.form.on("Purchase Receipt","validate",function(frm,cdt,cdn){
//This is required on client side also
for(var i=0; i < cur_frm.doc.items.length; i++) 
{
cur_frm.doc.items[i].warehouse = cur_frm.doc.selco_godown; 
}
})

