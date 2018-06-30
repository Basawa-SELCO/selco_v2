//cur_frm.add_fetch("party", "customer_name", "party_name"); 


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
        frm.set_df_property("selco_financed", "hidden", 1);
        frm.set_df_property("selco_financed", "reqd", 0);
        frm.set_df_property("selco_money_received_by", "hidden", 1);
        frm.set_df_property("selco_o_a_no", "hidden", 1);
        frm.set_df_property("selco_o_a_date", "hidden", 1);
        frm.set_df_property("paid_amount", "label", "Paid Amount");
    } else {
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
            cur_frm.set_value("selco_branch", "Bangalore Service Branch");
            //cur_frm.set_df_property("selco_branch", "read_only", true);
        } else if (frappe.user_info().email == "kundapura_service_center@selco-india.com") {
            cur_frm.set_value("selco_branch", "Kundapur Service Branch");
            //cur_frm.set_df_property("selco_branch", "read_only", true);
        } else if (frappe.user_info().email == "hassan_service_center@selco-india.com") {
            cur_frm.set_value("selco_branch", "Hassan Service Branch");
            //cur_frm.set_df_property("selco_branch", "read_only", true);
        } else if (frappe.user_info().email == "bellary_service_center@selco-india.com") {
            cur_frm.set_value("selco_branch", "Bellary Service Branch");
            //cur_frm.set_df_property("selco_branch", "read_only", true);
        } else if (frappe.user_info().email == "chitradurga_service_center@selco-india.com") {
            cur_frm.set_value("selco_branch", "Chitradurga Service Branch");
            //cur_frm.set_df_property("selco_branch", "read_only", true);
        } else if (frappe.user_info().email == "dharwad_service_center@selco-india.com") {
            cur_frm.set_value("selco_branch", "Dharwad Service Branch");
            //cur_frm.set_df_property("selco_branch", "read_only", true);
        } else if (frappe.user_info().email == "mysore_service_center@selco-india.com") {
            cur_frm.set_value("selco_branch", "Mysore Service Branch");
            //cur_frm.set_df_property("selco_branch", "read_only", true);
        } else if (frappe.user_info().email == "puttur_service_center@selco-india.com") {
            cur_frm.set_value("selco_branch", "Puttur Service Branch");
            //cur_frm.set_df_property("selco_branch", "read_only", true);
        } else if (frappe.user_info().email == "vijayapura_service_center@selco-india.com") {
            cur_frm.set_value("selco_branch", "Vijayapura Service Branch");
            //cur_frm.set_df_property("selco_branch", "read_only", true);
        } else if (frappe.user_info().email == "shimoga_service_center@selco-india.com") {
            cur_frm.set_value("selco_branch", "Shivamogga Service Branch");
            //cur_frm.set_df_property("selco_branch", "read_only", true);
        } 
    }

    frm.set_df_property("transaction_references", "hidden", (cur_frm.doc.mode_of_payment == "Cash") ? 1:0);
    
});


frappe.ui.form.on("Payment Entry", "selco_money_received_by", function(frm, cdt, cdn) {
    frm.set_value("paid_from_account_currency", frappe.defaults.get_default("currency"));
    frm.set_value("paid_to_account_currency", frappe.defaults.get_default("currency"));

    if (cur_frm.doc.selco_money_received_by == "Cash") {

        //cur_frm.set_value("mode_of_payment", "Cash");

        cur_frm.set_value("selco_money_received_by", "Cash");
        cur_frm.set_value("selco_financed", "NO");
        cur_frm.set_value("reference_no", "Cash");
        cur_frm.set_value("reference_date", frappe.datetime.get_today());
        cur_frm.set_df_property("reference_no", "read_only", true);

        cur_frm.set_df_property("reference_no", "hidden", 1);
        cur_frm.set_df_property("reference_no", "reqd", 0);
        cur_frm.set_df_property("reference_date", "hidden", 1);
        cur_frm.set_df_property("reference_date", "reqd", 0);
        cur_frm.set_df_property("selco_cheque_issuing_bank", "read_only", 1);
        cur_frm.set_df_property("selco_cheque_issuing_bank", "reqd", 0);

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

        // cur_frm.set_df_property("reference_no", "hidden", true);
        // cur_frm.set_df_property("selco_cheque_issuing_bank", "read_only", true);
        // cur_frm.set_df_property("selco_cheque_issuing_bank", "reqd", false);
        
    }

    if (cur_frm.doc.selco_money_received_by == "Cheque/DD" || cur_frm.doc.selco_money_received_by == "Online-NEFT/RTGS" ) {
        cur_frm.set_value("reference_date", undefined);
        //cur_frm.set_value("accounting_currency", "INR");
        //cur_frm.set_value("mode_of_payment", "Bank");
        cur_frm.set_df_property("reference_no", "hidden", 0);
        cur_frm.set_df_property("reference_no", "reqd", 1);
        cur_frm.set_df_property("reference_no", "read_only", false);
        cur_frm.set_value("reference_no", undefined);


        cur_frm.set_df_property("reference_date", "hidden", 0);
        cur_frm.set_df_property("reference_date", "reqd", 1);
        cur_frm.set_df_property("selco_cheque_issuing_bank", "read_only", 0);
        cur_frm.set_df_property("selco_cheque_issuing_bank", "reqd", 1);

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

        // cur_frm.set_df_property("reference_no", "hidden", false);
        // cur_frm.set_df_property("reference_date", "hidden", false);
        // cur_frm.set_df_property("selco_cheque_issuing_bank", "read_only", false);
        // cur_frm.set_df_property("selco_cheque_issuing_bank", "reqd", true);

    }
});

frappe.ui.form.on("Payment Entry", "selco_financed", function(frm, cdt, cdn) {
    if (cur_frm.doc.selco_financed == "YES") {
        cur_frm.set_df_property("selco_financing_institution", "read_only", false);
        cur_frm.set_df_property("selco_financing_institution_branch", "read_only", false);
        cur_frm.set_df_property("selco_financing_institution", "reqd", true);
        cur_frm.set_df_property("selco_financing_institution_branch", "reqd", true);
    } else {
        cur_frm.set_df_property("selco_financing_institution", "read_only", true);
        cur_frm.set_df_property("selco_financing_institution_branch", "read_only", true);
        cur_frm.set_df_property("selco_financing_institution", "reqd", false);
        cur_frm.set_df_property("selco_financing_institution_branch", "reqd", false);
    }
    cur_frm.refresh_field("selco_financing_institution");
});

//  frappe.ui.form.on("Payment Entry", "refresh", function(frm) {
// if (cur_frm.doc.__islocal == 1)
//  {
//  if (frappe.user_info().email == "bangalore_service_center@selco-india.com")
//  {
//  cur_frm.set_value("selco_branch", "Bangalore Service Branch");
//  cur_frm.set_df_property("selco_branch", "read_only", true);
//  } else if (frappe.user_info().email == "kundapura_service_center@selco-india.com")
//  {
//  cur_frm.set_value("selco_branch", "Kundapur Service Branch");
//  cur_frm.set_df_property("selco_branch", "read_only", true);
//  }else if (frappe.user_info().email == "puttur_service_center@selco-india.com")
//  {
//  cur_frm.set_value("selco_branch", "Puttur Service Branch");
//  cur_frm.set_df_property("selco_branch", "read_only", true);
//  }else if (frappe.user_info().email == "hassan_service_center@selco-india.com")
//  {
//  cur_frm.set_value("selco_branch", "Hassan Service Branch");
//  cur_frm.set_df_property("selco_branch", "read_only", true);
//  }else if (frappe.user_info().email == "bellary_service_center@selco-india.com")
//  {
//  cur_frm.set_value("selco_branch", "Ballari Service Branch");
//  cur_frm.set_df_property("selco_branch", "read_only", true);
//  }else if (frappe.user_info().email == "shimoga_service_center@selco-india.com")
//  {
//  cur_frm.set_value("selco_branch", "Shivamogga Service Branch");
//  cur_frm.set_df_property("selco_branch", "read_only", true);
//  }else if (frappe.user_info().email == "chitradurga_service_center@selco-india.com")
//  {
//  cur_frm.set_value("selco_branch", "Chitradurga Service Branch");
//  cur_frm.set_df_property("selco_branch", "read_only", true);
//  }else if (frappe.user_info().email == "dharwad_service_center@selco-india.com")
//  {
//  cur_frm.set_value("selco_branch", "Dharwad Service Branch");
//  cur_frm.set_df_property("selco_branch", "read_only", true);
//  }else if (frappe.user_info().email == "vijayapura_service_center@selco-india.com")
//  {
//  cur_frm.set_value("selco_branch", "Vijayapura Service Branch");
//  cur_frm.set_df_property("selco_branch", "read_only", true);
//  }else if (frappe.user_info().email == "mysore_service_center@selco-india.com")
//  {
//  cur_frm.set_value("selco_branch", "Mysore Service Branch");
//  cur_frm.set_df_property("selco_branch", "read_only", true);
//  }
//  }
//  })


frappe.ui.form.on("Payment Entry", "refresh", function(frm) {
cur_frm.set_query("selco_cheque_issuing_bank", function() {
    return {
        filters: [
            ['Financing Institution', 'name', '!=', 'SKDRDP']
        ]
    };
});
});


frappe.ui.form.on("Payment Entry", "payment_type", function(frm) {
    if (frm.doc.payment_type == "Receive"){
        frm.set_df_property("selco_money_received_by", "hidden", 0);
        frm.set_df_property("selco_financed", "hidden", 0);
        frm.set_df_property("selco_financed", "reqd", 1);
        frm.set_df_property("selco_money_received_by", "reqd", 1);
        frm.set_df_property("selco_o_a_no", "hidden", 0);
        frm.set_df_property("selco_o_a_date", "hidden", 0);
        frm.set_df_property("paid_amount", "label", "Received Amount");
    } else {
        frm.set_df_property("selco_financed", "hidden", 1);
        frm.set_df_property("selco_financed", "reqd", 0);
        frm.set_df_property("selco_money_received_by", "reqd", 0);
        frm.set_df_property("selco_money_received_by", "hidden", 1);
        frm.set_df_property("selco_o_a_no", "hidden", 1);
        frm.set_df_property("selco_o_a_date", "hidden", 1);
        frm.set_df_property("paid_amount", "label", "Paid Amount");
    }
});