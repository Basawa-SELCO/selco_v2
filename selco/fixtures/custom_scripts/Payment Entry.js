//cur_frm.add_fetch("branch", "collection_account", "paid_to"); 
cur_frm.add_fetch("party", "customer_name", "party_name"); 


frappe.ui.form.on("Payment Entry", "selco_financing_institution", function(frm) {
    cur_frm.set_query("selco_financing_institution_branch", function() {
        return {
            "filters": {
                "financing_institution": frm.doc.selco_financing_institution
            }
        };
    });
});


frappe.ui.form.on("Payment Entry", "refresh", function(frm) {
    if (frm.doc.payment_type == "Pay") {
        frm.set_df_property("selco_money_received_by", "hidden", 1);
        frm.set_df_property("selco_financed", "hidden", 1);
        frm.set_df_property("selco_financed", "reqd", 0);
        frm.set_df_property("selco_money_received_by", "reqd", 0);
        frm.set_df_property("selco_o_a_no", "hidden", 1);
        frm.set_df_property("selco_o_a_date", "hidden", 1);
        frm.set_df_property("paid_amount", "label", "Paid Amount");
    } else {
        frm.set_df_property("selco_money_received_by", "hidden", 0);
        frm.set_df_property("selco_financed", "hidden", 0);
        frm.set_df_property("selco_financed", "reqd", 1);
        frm.set_df_property("selco_money_received_by", "reqd", 1);
        frm.set_df_property("selco_o_a_no", "hidden", 0);
        frm.set_df_property("selco_o_a_date", "hidden", 0);
        frm.set_df_property("paid_amount", "label", "Received Amount");
    }

//cur_frm.doc.mode_of_payment = "Bank";

    cur_frm.set_query("mode_of_payment", function() {
        return {
    		filters: [
    			['Mode of Payment', 'mode_of_payment', 'in', 'Bank,Cash']
    		]
        };
    });
    cur_frm.fields_dict['references'].grid.get_field('reference_name').get_query = function(doc) {
        if ( cur_frm.doc.payment_type == "Receive") {
            return {
                "filters": {    
                    "customer": cur_frm.doc.party
                }
            };
        }

        if ( cur_frm.doc.payment_type == "Pay") {
            return {
                "filters": {
                    "supplier": cur_frm.doc.party
                }
            };
        }
    };
    cur_frm.fields_dict['references'].grid.get_field('reference_doctype').get_query = function(doc) {
        if ( cur_frm.doc.payment_type == "Receive") {
            return {
                "filters": {
                    "name": "Sales Invoice"
                }
            };
        }

        if ( cur_frm.doc.payment_type == "Pay") {
            return {
                "filters": {
                    "name": "Purchase Invoice"
                }
            };
        }
    };
    if (cur_frm.doc.__islocal == 1) {
        if (frappe.user_info().email == "bangalore_service_center@selco-india.com") {
            cur_frm.doc.selco_branch = "Bangalore Service Branch";
            cur_frm.set_df_property("selco_branch", "read_only", true);
        } else if (frappe.user_info().email == "kundapura_service_center@selco-india.com") {
            cur_frm.doc.selco_branch = "Kundapur Service Branch";
            cur_frm.set_df_property("selco_branch", "read_only", true);
        }
    }
});


frappe.ui.form.on("Payment Entry", "selco_money_received_by", function(frm, cdt, cdn) {
    if (cur_frm.doc.selco_money_received_by == "Cash") {

        cur_frm.set_value("mode_of_payment", "Cash");

        cur_frm.set_value("selco_money_received_by", "Cash");
        cur_frm.set_value("selco_financed", "NO");
        cur_frm.set_value("reference_no", "Cash");
        cur_frm.set_df_property("reference_no", "read_only", true);

        var d = locals[cdt][cdn];
        frappe.call({
        	"method": "frappe.client.get",
        	args: {
        		doctype: "Branch",
        		name: d.selco_branch
        	},
        	callback: function (data) {
        		frappe.model.set_value(d.doctype, d.name, "paid_to", data.message.selco_collection_account_cash);
        	}
        });

        cur_frm.set_df_property("reference_no", "hidden", true);
        cur_frm.set_df_property("reference_date", "hidden", true);
        cur_frm.set_df_property("selco_cheque_issuing_bank", "read_only", true);
        cur_frm.set_df_property("selco_cheque_issuing_bank", "reqd", false);
    }

    if (cur_frm.doc.selco_money_received_by == "Cheque/DD" || cur_frm.doc.selco_money_received_by == "Online-NEFT/RTGS" ) {
        cur_frm.set_value("reference_no", "");

        cur_frm.set_value("mode_of_payment", "Bank");

        var d = locals[cdt][cdn];
        frappe.call({
        	"method": "frappe.client.get",
        	args: {
        		doctype: "Branch",
        		name: d.selco_branch
        	},
        	callback: function (data) {
        		frappe.model.set_value(d.doctype, d.name, "paid_to", data.message.selco_collection_account);
        	}
        });

        cur_frm.set_df_property("reference_no", "hidden", false);
        cur_frm.set_df_property("reference_date", "hidden", false);
        cur_frm.set_df_property("selco_cheque_issuing_bank", "read_only", false);
        cur_frm.set_df_property("selco_cheque_issuing_bank", "reqd", true);
    }
});

frappe.ui.form.on("Payment Entry", "selco_financed", function(frm, cdt, cdn) {
    if (cur_frm.doc.selco_financed == "YES") {
        cur_frm.set_df_property("selco_financing_institution", "read_only", false);
        cur_frm.refresh_field("selco_financing_institution");
        cur_frm.set_df_property("selco_financing_institution_branch", "read_only", false);
        cur_frm.set_df_property("selco_financing_institution", "reqd", true);
        cur_frm.set_df_property("selco_financing_institution_branch", "reqd", true);
    } else {
        cur_frm.set_df_property("selco_financing_institution", "read_only", true);
        cur_frm.set_df_property("selco_financing_institution_branch", "read_only", true);
        cur_frm.set_df_property("selco_financing_institution", "reqd", false);
        cur_frm.set_df_property("selco_financing_institution_branch", "reqd", false);
    }
});

frappe.ui.form.on("Payment Entry", "refresh", function(frm) {
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
})

frappe.ui.form.on("Payment Entry", "refresh", function (frm, cdt, cdn) {
  cur_frm.set_query("party", function () {
    return { 
      query: "erpnext.controllers.queries.customer_query",
      searchfield: "selco_customer_contact_number"
    }
  });
});

frappe.ui.form.on("Payment Entry", "refresh", function(frm) {
    {
        cur_frm.add_custom_button(__("Create New Customer"), cur_frm.cscript.create_new_customer);
    }
})



cur_frm.cscript.create_new_customer = function() {
    var cust_name = "";
    console.log("clicked on New Customer");
    var d = new frappe.ui.Dialog({
        title: __("Create New Customer"),
        fields: [{
                "fieldname": "selco_branch",
                "fieldtype": "Link",
                "label": __("Branch"),
                options: "Branch",
                reqd: 1,
                default : cur_frm.doc.selco_branch
            }, 
            {
                "fieldname": "customer_group",
                "fieldtype": "Link",
                "label": __("Customer Group"),
                options: "Customer Group",
                reqd: 1,

            },

            {
                "fieldname": "customer_name",
                "fieldtype": "Data",
                "label": __("Full Name"),
                reqd: 1,

            },
            {
                "fieldname": "selco_customer_contact_number",
                "fieldtype": "Data",
                "label": __("Customer Contact Number"),

            },
            {
                "fieldname": "selco_landline_mobile_2",
                "fieldtype": "Data",
                "label": __("Landline / Mobile 2"),

            },

            {
                "fieldname": "selco_gender",
                "fieldtype": "Select",
                "label": __("Gender"),
                "default": ["Male"],
                "options": "Male\nFemale"

            },

            {
                "fieldname": "selco_electrification_status",
                "fieldtype": "Select",
                "label": __("Electrification Status"),
                "options": "Electrified - Rural\nElectrified - Semi Urban\nElectrified - Urban\nElectrified - Migrant\nElectrified - Tribal\nUnelectrified - Rural\nUnelectrified - Semi Urban\nUnelectrified - Urban\nUnelectrified - Migrant\nUnelectrified - Tribal"
            },



            {
                fieldname: "fetch",
                "label": __("Create New Customer"),
                "fieldtype": "Button"
            }

        ]
    });

    d.get_input("fetch").on("click", function() {
        var values = d.get_values();
        if (values.selco_electrification_status) {
            var local_es = values.selco_electrification_status
        } else {
            local_es = ""
        }
       

        if (values.selco_landline_mobile_2) {
            var local_land = values.selco_landline_mobile_2
        } else {
            local_land = ""
        }

        if (values.selco_customer_contact_number) {
            var local_mob = values.selco_customer_contact_number
        } else {
            local_mob = ""
        }




        frappe.call({
            "method": "selco.selco.selco_customizations.selco_create_customer",
            "args": {
                "selco_branch": values.selco_branch,
               
                "customer_group": values.customer_group,
                "customer_name": values.customer_name,
                "selco_customer_contact_number": local_mob,
                "selco_landline_mobile_2": local_land,
                "selco_gender": values.selco_gender,
                "selco_electrification_status": local_es
            },
            callback: function(r) {
                console.log(r);
                d.hide();
                cust_name = r.message[0]
                cust_name_str = r.message[1]

                cur_frm.set_value("party", cust_name);
                cur_frm.set_value("party_name", cust_name_str);

            }
        });

    })
    d.show();
}

frappe.ui.form.on("Payment Entry", "refresh", function(frm) {
cur_frm.set_query("selco_cheque_issuing_bank", function() {
    return {
        filters: [
            ['Financing Institution', 'name', '!=', 'SKDRDP']
        ]
    };
});
})


frappe.ui.form.on("Payment Entry", "refresh", function(frm) {
    {
        cur_frm.add_custom_button(__("Add New Address"), cur_frm.cscript.add_new_address);
    }
})
cur_frm.cscript.add_new_address = function() {
    var d = new frappe.ui.Dialog({
        title: __("Add New Address"),
        fields: [{
                "fieldname": "selco_branch",
                "fieldtype": "Link",
                "label": __("Branch"),
                options: "Branch",
                reqd: 1,
                default : cur_frm.doc.selco_branch

             }, 
             {
                "fieldname": "address_type",
               "fieldtype": "Select",
                "label": __("Address Type"),
                default : "Billing",
               "options": "Billing\n Shipping\n Office\n Personal\n Plant\n Postal\n Shop\n Subsidiary\n Warehouse\n Other"
                 },

              {
                "fieldname": "address_line1",
                "fieldtype": "Data",
                "label": __("Address Line 1"),
                reqd: 1,

            },


            {
                "fieldname": "address_line2",
                "fieldtype": "Data",
                "label": __("Address Line 2"),
                reqd: 1,

            },


              {
                "fieldname": "city",
                "fieldtype": "Data",
                "label": __("City/Town"),
                 reqd: 1,
              },
             {
                "fieldname": "selco_district",
               "fieldtype": "Select",
                "label": __("District"),
               "options": "Bagalkote \n Belgaum \n Bellary\n Bengaluru Rural\n Bengaluru\n Bidar\nChamarajanagar\nChikkaballapur\nChikkamagaluru\nChitradurga\nDakshina Kannada\nDavanagere\nDharwad\nGadag\nHassan\nHaveri\nHyderabad\nKalaburagi\nKarwar\nKasaragod\nKodau\nKolar\nKoppal\nMandya\nMysuru\nPudukottai\nRaichur\nRamanagara\nShivamogga\nSolapur\nTumakuru\nUdupi\nUttara Kannada\nVijayapura\nYadgir\nMunger\nPatna\nThane\nNandurbar\nAriyalur\nChennai\nCoimbatore\nCuddalore\nDindigul\nErode\nKanchipuram\nKanyakumari\nKarur\nMadurai\nNagapattinam\nNamakkal\nRamanahapuram\nSalem\nSivagangai\nThanjavur\nTheni\nThiruppur\nTrichi\nViridhunagar\nNilgiris\nDharmapuri",
             reqd: 1
                 },

             {
                "fieldname": "country",
                "fieldtype": "Link",
                "label": __("Country"),
                options: "Country",
                default : "India",
                reqd: 1,

            },
         {
                "fieldname": "customer",
                "fieldtype": "Link",
                "label": __("Customer"),
                options: "Customer",
                reqd: 1,
                default : cur_frm.doc.party


            },{
                "fieldname": "address_title",
               "fieldtype": "Data",
                "label": __("Address Title"),
                 default :"jkl",
                 read_only:1
                 },
            {
                fieldname: "fetch",
                "label": __("Add New Address"),
                "fieldtype": "Button"
            },
       ]
    });
  
  d.get_input("fetch").on("click", function() {
              var values = d.get_values();console.log(values.address_title);
              frappe.call({
                  "method": "selco.selco.selco_customizations.selco_add_new_address",
                  "args": {
                      "selco_branch": values.selco_branch,
                      "address_type": values.address_type,
	              	"address_line1": values.address_line1,
                      "address_line2": values.address_line2,
                      "city": values.city,
                      "selco_district": values.selco_district,
                      "country": values.country,
                      "customer": values.customer,
                       "address_title":values.address_title
                  },
                  callback: function(r) {
                      d.hide();
			address_name = r.message[0]
                        address_display = r.message[0]
cur_frm.set_value("selco_recipient_address_link",r.message[0]);
cur_frm.set_value("selco_recipient_address",r.message[1]);


                  }

              })
              })

              d.show();
          }

