# -*- coding: utf-8 -*-
# Copyright (c) 2015, Selco and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import now,now_datetime
import operator
from erpnext.accounts.party import get_party_account, get_due_date
from datetime import datetime
from datetime import timedelta
from frappe.utils import cint

class SelcoCustomizations(Document):
    pass

@frappe.whitelist()
def service_call_info():
    #triggerS aT 12 O'clocK

    if str(frappe.utils.data.nowtime().split(":")[0]) == '13':
        info=frappe.db.sql("""SELECT B.day1,B.day2,B.day3,B.day4,B.day5,B.day6,B.day7,B.day8,B.day9,B.day10,B.day11,B.day12,B.day13,B.day14,B.day15,B.day16,B.day17,B.day18,B.day19,B.day20,B.day21,B.day22,B.day23,B.day24,B.day25,B.day26,B.day27,B.day28,B.day29,B.day30,B.day31,B.day1+B.day2+B.day3+B.day4+B.day5+B.day6+B.day7+B.day8+B.day9+B.day10+B.day11+B.day12+B.day13+B.day14+B.day15+B.day16+B.day17+B.day18+B.day19+B.day20+B.day21+B.day22+B.day23+B.day24+B.day25+B.day26+B.day27+B.day28+B.day29+B.day30+B.day31,B.service_person FROM `tabService Call` AS A INNER JOIN `tabService Call Details` AS B ON A.name=B.parent WHERE A.month=MONTHNAME(MONTH(ADDDATE(CURDATE(), -1))*100) """,as_list=1)
        #0-30 indeX oF numbeR oF callS
        #31 totaL callS
        #32 servicE persoN

        todate=int(str((datetime.now()+timedelta(days=-1)).date()).split("-")[2])
        #yesterday'S datE
        i=0
        while i<len(info) :
            if frappe.db.get_value("Service Person",info[i][32],"send_sms") :
                cn=str(frappe.db.get_value("Service Person",info[i][32],"contact_number"))+"@sms.textlocal.in"
                frappe.sendmail(
                    recipients=[cn],
                    subject="Number of Service Calls",
                    message="Dear "+info[i][32]+". You have made "+str(int(info[i][todate-1]))+" service calls yesterday and a total of "+str(int(info[i][31]))+" service calls till yesterday!"
                    )
            i=i+1

def month_service_person_unique(doc,method):
    for d in doc.service_call_details:
        if frappe.db.sql("""SELECT A.month,B.service_person FROM `tabService Call` AS A, `tabService Call Details` AS B WHERE A.name=B.parent AND A.month=%s AND B.service_person=%s """,(doc.month,d.service_person),as_list=1) :
            frappe.throw("Repeated Record for "+d.service_person+" in "+doc.month)

@frappe.whitelist()
def selco_issue_before_insert(doc,method):
    doc.naming_series = frappe.db.get_value("Branch",doc.selco_branch,"selco_customer_complaint_naming_series")

@frappe.whitelist()
def selco_warranty_claim_validate(doc,method):
    doc.selco_senior_service_manager_email_id = frappe.db.get_value("Branch",doc.selco_branch,"selco_service_manager_email_id")
    doc.selco_godown_email_id = frappe.db.get_value("Branch",doc.selco_branch,"selco_godown_email_id")

@frappe.whitelist()
def selco_issue_validate1(doc,method):
    if doc.workflow_state =="Complaint Open":
        if not doc.selco_customer_address:
            frappe.throw("Please Enter Customer Address")
    if doc.workflow_state =="Complaint Closed By Branch":
        if not doc.selco_service_record:
            frappe.throw(("Please Enter Service Record Details Before Closing the Complaint"))
        cur_date = now_datetime().date()
        doc.selco_complaint_closed_date = cur_date
        doc.status = "Closed"
        doc.resolution_date = now()


@frappe.whitelist()
def selco_warranty_claim_updates(doc,method):
    var4 = frappe.db.get_value("Warranty Claim", {"complaint_number": (doc.complaint_number)})
    var5 = unicode(var4) or u''
    var6 = frappe.db.get_value("Warranty Claim", {"complaint_number": (doc.complaint_number)}, "customer_full_name")
    if var5 != "None" and doc.name != var5:
        frappe.throw("Warranty Claim for complaint " + doc.complaint_number + " already exists. <br /> Warranty Claim Number : " + var5 + "<br /> Customer Name : " + var6 + "<br /> You cannot link same complaint for tow warranty claims.<br />Please create another complaint.")
    if doc.workflow_state =="Dispatched From Godown":
        doc.status = "Closed"
    """if doc.complaint_number and doc.workflow_state == "Warranty Claim Format Raised - WC":
        complaint = frappe.get_doc("Issue",doc.complaint_number)
        complaint.warranty_claim_number = doc.name
        complaint.save()"""

@frappe.whitelist()
def get_address_display(address_dict):
    if not address_dict:
        return

    if not isinstance(address_dict, dict):
        address_dict = frappe.db.get_value("Address", address_dict, "*", as_dict=True) or {}

    name, template = get_address_templates(address_dict)

    try:
        return frappe.render_template(template, address_dict)
    except TemplateSyntaxError:
        frappe.throw(_("There is an error in your Address Template {0}").format(name))

@frappe.whitelist()
def selco_delivery_note_validates(doc,method):
    selco_warehouse  = frappe.db.get_value("Branch",doc.selco_branch,"selco_warehouse")
    selco_cost_center = frappe.db.get_value("Branch",doc.selco_branch,"selco_cost_center")
    frappe.msgprint(selco_warehouse)
    frappe.msgprint(selco_cost_center)
    for d in doc.get('items'):
        d.warehouse = selco_warehouse
        d.cost_center = selco_cost_center
        if not d.rate:
            d.rate = frappe.db.get_value("Item Price",{"price_list": "Branch Sales","item_code":d.item_code}, "price_list_rate")
@frappe.whitelist()
def selco_delivery_note_before_insert(doc,method):
    if doc.is_return:
        doc.naming_series = "DC-RET/"
    else:
        doc.naming_series = frappe.db.get_value("Branch",doc.selco_branch,"selco_delivery_note_naming_series")
    selco_warehouse  = frappe.db.get_value("Branch",doc.selco_branch,"selco_warehouse")
    selco_cost_center = frappe.db.get_value("Branch",doc.selco_branch,"selco_cost_center")
    for d in doc.get('items'):
        d.warehouse = selco_warehouse
        d.cost_center = selco_cost_center
        if not d.rate:
            d.rate = frappe.db.get_value("Item Price",{"price_list": "Branch Sales","item_code":d.item_code}, "price_list_rate")

@frappe.whitelist()
def selco_material_request_before_insert(doc,method):
    doc.naming_series = frappe.db.get_value("Branch",doc.selco_branch,"selco_material_request_naming_series")
    local_warehouse = frappe.db.get_value("Branch",doc.selco_branch,"selco_git_warehouse")
    for d in doc.get('items'):
        if not d.warehouse:
               d.warehouse = local_warehouse

@frappe.whitelist()
def selco_material_request_validate(doc,method):
    #frappe.msgprint("selco_material_request_updates")
    doc.items.sort(key=operator.attrgetter("item_code"), reverse=False)

    selco_material_approved_and_dispatched(doc,method)

    if doc.workflow_state == "Partially Dispatched From Godown - IBM":
        flag = "N"
        for d in doc.get('items'):
            if d.selco_dispatched_quantity != 0:
                flag = "Y"
        for d in doc.get('items'):
            if flag != "Y":
                d.dispatched_quantity = d.qty
    if doc.workflow_state == "Dispatched From Godown - IBM":
        for d in doc.get('items'):
            d.selco_dispatched_quantity = d.qty
    doc.selco_branch_credit_limit = frappe.db.get_value("Branch",doc.selco_branch,"selco_branch_credit_limit")
    doc.selco_senior_sales_manager_email_id = frappe.db.get_value("Branch",doc.selco_branch,"selco_senior_sales_manager_email_id")
    doc.selco_godown_email_id = frappe.db.get_value("Branch",doc.selco_branch,"selco_godown_email_id")
    doc.selco_agms_email_id = frappe.db.get_value("Branch",doc.selco_branch,"selco_agm_email_id")
    #End of Insert By Poorvi on 08-02-2017

@frappe.whitelist()
def selco_material_approved_and_dispatched(doc,method):
    #frappe.msgprint("selco_material_approved_and_dispatched")

    if doc.workflow_state == "Approved - IBM":
         doc.selco_approved_time = now()

    elif doc.workflow_state == "Dispatched From Godown - IBM":
        doc.selco_dispatched_time = now()

@frappe.whitelist()
def selco_purchase_receipt_before_insert(doc,method):
    # BRANCH2WAREHOUSE
    # local_branch = frappe.db.get_value("Warehouse",doc.selco_godown,"selco_branch")
    # doc.naming_series = frappe.db.get_value("Branch",local_branch,"selco_mrn_naming_series")
    doc.naming_series = frappe.db.get_value("Warehouse",doc.selco_godown,"selco_mrn_naming_series")

@frappe.whitelist()
def selco_purchase_order_before_insert(doc,method):
    # BRANCH2WAREHOUSE
    # local_branch = frappe.db.get_value("Warehouse",doc.selco_godown,"selco_branch")
    # doc.naming_series = frappe.db.get_value("Branch",local_branch,"selco_po_naming_series")
    doc.naming_series = frappe.db.get_value("Warehouse", doc.selco_godown, "selco_po_naming_series")


@frappe.whitelist()
def selco_purchase_order_validate(doc,method):
    godown_address_ret = get_default_address_name_and_display("Warehouse", doc.selco_godown)
    doc.selco_godown_address = godown_address_ret.address_name
    doc.selco_godown_address_details = godown_address_ret.address_display

    doc.selco_godown_email = frappe.db.get_value("Warehouse",doc.selco_godown,"selco_godown_email")
    
    doc.base_rounded_total= round(doc.base_grand_total)
    advance_local = doc.base_rounded_total * (float(doc.selco_advance_percentage_1) / 100)
    advance_local = round(advance_local)
    balance_local = doc.base_rounded_total - advance_local
    doc.selco_advance_details_currency=advance_local
    doc.selco_balance_details_currency=balance_local

    for d in doc.get('items'):
        d.warehouse = doc.selco_godown


@frappe.whitelist()
def selco_purchase_receipt_validate(doc,method):
    # BRANCH2WAREHOUSE
    # local_branch = frappe.db.get_value("Warehouse",doc.selco_godown,"selco_branch")
    # selco_cost_center = frappe.db.get_value("Branch",local_branch,"selco_cost_center")
    godown_cost_center = frappe.db.get_value("Warehouse", doc.selco_godown, "selco_cost_center")

    for d in doc.get('items'):
        d.cost_center = godown_cost_center #BRANCH2WAREHOUSE
        d.warehouse = doc.selco_godown 
    for d in doc.get('taxes'):
        d.cost_center = godown_cost_center #BRANCH2WAREHOUSE


    doc.set('selco_purchase_receipt_item_print', [])

    flag=0
    row = doc.append('selco_purchase_receipt_item_print', {})
    row.selco_item_code = doc.items[0].item_code
    row.selco_item_name = doc.items[0].item_name
    row.selco_received_quantity = doc.items[0].received_qty
    row.selco_accepted_quantity = doc.items[0].qty
    row.selco_rejected_quantity = doc.items[0].rejected_qty
    row.selco_rate = doc.items[0].rate

    for i,rowi in enumerate(doc.get('items')):
        if (i != 0):
            for j,rowj in enumerate(doc.get('selco_purchase_receipt_item_print')):
                if (doc.items[i].item_code == doc.selco_purchase_receipt_item_print[j].selco_item_code and doc.items[i].item_name == doc.selco_purchase_receipt_item_print[j].selco_item_name):
                   flag=1
                   doc.selco_purchase_receipt_item_print[j].selco_received_quantity = doc.selco_purchase_receipt_item_print[j].selco_received_quantity+doc.items[i].received_qty
                   doc.selco_purchase_receipt_item_print[j].selco_accepted_quantity = doc.selco_purchase_receipt_item_print[j].selco_accepted_quantity+doc.items[i].qty
                   doc.selco_purchase_receipt_item_print[j].selco_rejected_quantity = doc.selco_purchase_receipt_item_print[j].selco_rejected_quantity+doc.items[i].rejected_qty

            if(flag!= 1):
               r = doc.append('selco_purchase_receipt_item_print', {})
               r.selco_item_code = doc.items[i].item_code
               r.selco_item_name = doc.items[i].item_name
               r.selco_received_quantity = doc.items[i].received_qty
               r.selco_accepted_quantity = doc.items[i].qty
               r.selco_rejected_quantity = doc.items[i].rejected_qty
               r.selco_rate = doc.items[i].rate
               #frappe.msgprint(str(flag))
            flag=0
    po_list = []
    po_list_date = []
    for item_selco in doc.items:
        if item_selco.purchase_order not in po_list:
            po_list.append(item_selco.purchase_order)
            po_list_date.append(frappe.utils.formatdate(frappe.db.get_value('Purchase Order', item_selco.purchase_order, 'transaction_date'),"dd-MM-yyyy"))
    doc.selco_list_of_po= ','.join([str(i) for i in po_list])
    doc.selco_list_of_po_date= ','.join([str(i) for i in po_list_date])
    #End of Insert By basawaraj On 7th september for printing the list of PO when PR is done by importing items from multiple PO
    if doc.selco_type_of_purchase == "Normal":
        for d in doc.get('items'):
            if not d.purchase_order :
                frappe.throw("Purchase Order Is Mandatory")





@frappe.whitelist()
def selco_stock_entry_updates(doc,method):

    selco_cost_center = frappe.db.get_value("Branch",doc.selco_branch,"selco_cost_center")
    selco_selco_warehouse = frappe.db.get_value("Branch",doc.selco_branch,"selco_warehouse")
    selco_repair_warehouse = frappe.db.get_value("Branch",doc.selco_branch,"selco_repair_warehouse")

    if not selco_cost_center:
        frappe.throw("Please set Cost Center in the selected Branch")
    if not selco_selco_warehouse:
        frappe.throw("Please set Warehouse in the selected Branch")
    if not selco_repair_warehouse:
        frappe.throw("Please set Repair Warehouse in the selected Branch")

    if doc.purpose=="Material Transfer":
        if doc.selco_inward_or_outward=="Inward" and doc.selco_type_of_stock_entry == "GRN":
            doc.naming_series = frappe.db.get_value("Branch",doc.selco_branch,"selco_receipt_note_naming_series")

            if doc.selco_type_of_material=="Good Stock":
                doc.from_warehouse = "SELCO GIT - SELCO"
                doc.to_warehouse = selco_selco_warehouse
                for d in doc.get('items'):
                    d.cost_center = selco_cost_center
                    d.from_warehouse = "SELCO GIT - SELCO"
                    d.to_warehouse = selco_selco_warehouse

            else:
                for d in doc.get('items'):
                    d.s_warehouse = "SELCO GIT Repair - SELCO"
                    d.t_warehouse = selco_repair_warehouse
                    d.cost_center = selco_cost_center
                    d.is_sample_item = 1
        elif doc.selco_inward_or_outward=="Inward" and doc.selco_type_of_stock_entry == "Demo - Material Return":
            for d in doc.get('items'):
                d.cost_center = selco_cost_center
                d.s_warehouse = "Demo Warehouse - SELCO"
                d.t_warehouse = selco_selco_warehouse
        elif doc.selco_inward_or_outward=="Outward" and doc.selco_type_of_stock_entry== "Outward DC":
            doc.naming_series = frappe.db.get_value("Branch",doc.selco_branch,"selco_delivery_note_naming_series")
            if doc.selco_type_of_material=="Good Stock":
                doc.from_warehouse = selco_selco_warehouse
                frappe.msgprint(selco_selco_warehouse)
                doc.to_warehouse = "SELCO GIT - SELCO"
                for d in doc.get('items'):
                    d.s_warehouse = selco_selco_warehouse
                    d.t_warehouse = "SELCO GIT - SELCO"
                    d.cost_center = selco_cost_center
            else:
                doc.from_warehouse = selco_repair_warehouse
                doc.to_warehouse = "SELCO GIT Repair - SELCO"
                for d in doc.get('items'):
                    d.s_warehouse = selco_repair_warehouse
                    d.t_warehouse = "SELCO GIT Repair - SELCO"
                    d.cost_center = selco_cost_center
                    d.is_sample_item = 1
        elif doc.selco_inward_or_outward=="Outward" and doc.selco_type_of_stock_entry== "Demo - Material Issue":
            doc.naming_series = frappe.db.get_value("Branch",doc.selco_branch,"selco_delivery_note_naming_series")
            for d in doc.get('items'):
                d.s_warehouse = selco_selco_warehouse
                d.t_warehouse = "Demo Warehouse - SELCO"
                d.cost_center = selco_cost_center
    elif doc.purpose=="Material Receipt":
        doc.naming_series = frappe.db.get_value("Branch",doc.selco_branch,"selco_rejection_in_naming_series")
        doc.to_warehouse = selco_repair_warehouse
        for d in doc.get('items'):
            d.t_warehouse = selco_repair_warehouse
            d.cost_center = selco_cost_center
            d.is_sample_item = 1
    elif doc.purpose=="Material Issue":
        doc.naming_series = frappe.db.get_value("Branch",doc.selco_branch,"selco_rejection_out_naming_series")
        doc.from_warehouse = selco_repair_warehouse
        for d in doc.get('items'):
            d.f_warehouse = selco_repair_warehouse
            d.cost_center = selco_cost_center
            d.is_sample_item = 1
    elif doc.purpose=="Repack":
        if doc.selco_stock_journal == 0:
            doc.naming_series = frappe.db.get_value("Branch",doc.selco_branch,"selco_bill_of_material_naming_series")
        else:
            doc.naming_series = "SJ/HO/17-18/"

        for d in doc.get('items'):
            d.cost_center = selco_cost_center
            d.s_warehouse = selco_selco_warehouse
            #d.t_warehouse = selco_selco_warehouse #Repack, so do not set target warehouse for these items.
            #if d.t_warehouse:
            d.basic_rate = 0

        #Repack, so Clear source warehouse. Set only target warehouse on last line item.
        doc.get('items')[-1:][0].s_warehouse = None
        doc.get('items')[-1:][0].t_warehouse = selco_selco_warehouse

    if doc.selco_type_of_stock_entry == "Outward DC":
        doc.selco_recipient_email_id = frappe.db.get_value("Branch",doc.selco_being_dispatched_to,"selco_branch_email_id")

@frappe.whitelist()
def selco_stock_entry_validate(doc,method):
    from frappe.contacts.doctype.address.address import get_address_display, get_default_address
    if doc.selco_type_of_stock_entry == "Outward DC":
        local_warehouse = frappe.db.get_value("Branch",doc.selco_being_dispatched_to,"selco_warehouse")
        doc.selco_recipient_address_link = get_default_address("Warehouse", local_warehouse) #frappe.db.get_value("Warehouse",local_warehouse,"address")
        doc.selco_recipient_address = "<b>" + doc.selco_being_dispatched_to.upper() + " BRANCH</b><br>"
        doc.selco_recipient_address+= "SELCO SOLAR LIGHT PVT. LTD.<br>"
        doc.selco_recipient_address+= str(get_address_display(doc.selco_recipient_address_link))
    elif doc.selco_type_of_stock_entry == "GRN":
        sender = frappe.db.get_value("Stock Entry",doc.selco_suppliers_ref,"selco_branch")
        frappe.msgprint(doc.selco_suppliers_ref)
        sender_warehouse = frappe.db.get_value("Branch",sender,"selco_warehouse")
        doc.sender_address_link = get_default_address("Warehouse", sender_warehouse) #frappe.db.get_value("Warehouse",sender_warehouse,"address")
        doc.sender_address = "<b>" + str(sender) + " SELCO BRANCH</b><br>"
        doc.sender_address += "SELCO SOLAR LIGHT PVT. LTD.<br>"
        doc.sender_address += str(get_address_display(doc.sender_address_link))

@frappe.whitelist()
def get_items_from_outward_stock_entry(selco_doc_num,selco_branch):
    selco_var_dc = frappe.get_doc("Stock Entry",selco_doc_num)
    if selco_var_dc.selco_type_of_stock_entry != "Demo - Material Issue" and selco_var_dc.selco_being_dispatched_to != selco_branch:
        frappe.throw("Incorrect DC Number");
    from_warehouse = selco_var_dc.to_warehouse
    if selco_var_dc.selco_type_of_material=="Good Stock":
        to_warehouse = frappe.db.get_value("Branch",selco_var_dc.selco_being_dispatched_to,"selco_warehouse")
    else:
        to_warehouse = frappe.db.get_value("Branch",selco_var_dc.selco_being_dispatched_to,"selco_repair_warehouse")
    return { 'dc' : selco_var_dc,'from_warehouse' : from_warehouse, 'to_warehouse' :to_warehouse }

@frappe.whitelist()
def get_items_from_rejection_in(selco_rej_in,selco_branch):
    selco_var_dc = frappe.get_doc("Stock Entry",selco_rej_in)
    return { 'dc' : selco_var_dc }

    """frappe.msgprint("Button Clicked");
    selco_cost_center = frappe.db.get_value("Branch",selco_branch,"cost_center")
    selco_selco_warehouse = frappe.db.get_value("Branch",selco_branch,"selco_warehouse")
    selco_repair_warehouse = frappe.db.get_value("Branch",selco_branch,"repair_warehouse")
    outward_dc = frappe.get_doc("Stock Entry",selco_doc_num)
    if outward_dc.selco_type_of_material=="Good Stock":
        for d in outward_dc.get('items'):
            d.s_warehouse = "SELCO GIT - SELCO"
            d.t_warehouse = selco_selco_warehouse
            d.cost_center = selco_cost_center
    else:
        for d in outward_dc.get('items'):
            d.s_warehouse = "SELCO GIT Repair - SELCO"
            d.t_warehouse = selco_selco_warehouse
            d.cost_center = selco_cost_center"""

@frappe.whitelist()
def selco_customer_before_insert(doc,method):
    doc.naming_series = frappe.db.get_value("Branch",doc.selco_branch,"selco_customer_naming_series")

@frappe.whitelist()
def selco_customer_validate(doc,method):
    #Suspended for Import
    # if not ( doc.selco_customer_contact_number or doc.selco_landline_mobile_2 ):
    #     frappe.throw("Enter either Customer Contact Number ( Mobile 1 ) or Mobile 2 / Landline")
    if doc.selco_customer_contact_number:
        if len(doc.selco_customer_contact_number) != 10:
            frappe.throw("Invalid Customer Contact Number ( Mobile 1 ) - Please enter exact 10 digits of mobile no ex : 9900038803")
        selco_validate_if_customer_contact_number_exists(doc.selco_customer_contact_number,doc.name)
    if doc.selco_landline_mobile_2:
        selco_validate_if_customer_contact_number_exists(doc.selco_landline_mobile_2,doc.name)

def selco_validate_if_customer_contact_number_exists(contact_number,customer_id):
    #frappe.msgprint(frappe.session.user)
    var4 = frappe.db.get_value("Customer", {"selco_customer_contact_number": (contact_number)})
    var5 = unicode(var4) or u''
    var6 = frappe.db.get_value("Customer", {"selco_customer_contact_number": (contact_number)}, "customer_name")
    if var5 != "None" and customer_id != var5:
        frappe.throw("Customer with contact no " + contact_number + " already exists \n Customer ID : " + var5 + "\n Lead Name : " + var6)

    var14 = frappe.db.get_value("Customer", {"selco_landline_mobile_2": (contact_number)})
    var15 = unicode(var14) or u''
    var16 = frappe.db.get_value("Customer", {"selco_landline_mobile_2": (contact_number)}, "customer_name")
    if var15 != "None" and customer_id != var15:
        frappe.throw("Customer with contact no " + contact_number + " already exists \n Customer ID : " + var15 + "\n Lead Name : " + var16)


@frappe.whitelist()
def selco_sales_invoice_before_insert(doc,method):

    doc.selco_customer_contact_number = frappe.db.get_value("Customer",doc.customer,"selco_customer_contact_number")
    doc.selco_customer_tin_number = frappe.db.get_value("Customer",doc.customer,"selco_customer_tin_number")
    if doc.is_return == 1:
        doc.naming_series = frappe.db.get_value("Branch",doc.selco_branch,"selco_credit_note_naming_series")
    else:
        if doc.selco_type_of_invoice == "System Sales Invoice" or doc.selco_type_of_invoice == "Spare Sales Invoice":
            doc.naming_series = frappe.db.get_value("Branch",doc.selco_branch,"selco_sales_invoice_naming_series")
        elif doc.selco_type_of_invoice == "Service Bill":
            doc.naming_series = frappe.db.get_value("Branch",doc.selco_branch,"selco_service_bill_naming_series")
        elif doc.selco_type_of_invoice == "Bill of Sale":
            doc.naming_series = frappe.db.get_value("Branch",doc.selco_branch,"selco_bill_of_sales_naming_series")

@frappe.whitelist()
def selco_sales_invoice_validate(doc,method):
    #selco_warehouse  = frappe.db.get_value("Branch",doc.branch,"selco_warehouse")
    selco_cost_center = frappe.db.get_value("Branch",doc.selco_branch,"selco_cost_center")
    for d in doc.get('items'):
        d.cost_center = selco_cost_center
        d.income_account = doc.selco_sales_account
    for d in doc.get('taxes'):
        d.cost_center = selco_cost_center
    for i,c in enumerate(doc.get('taxes')):
        if doc.taxes[i].account_head == "Discount Karnataka 14.5% - SELCO":
           if doc.taxes[i].tax_amount>0:
              doc.taxes[i].tax_amount = doc.taxes[i].tax_amount * -1
def selco_payment_entry_before_insert(doc,method):
    if doc.payment_type == "Receive":
        doc.naming_series = frappe.db.get_value("Branch",doc.selco_branch,"selco_receipt_naming_series")
        if doc.mode_of_payment == "Bank":
            if doc.selco_amount_credited_to_platinum_account == 1:
                doc.paid_to = frappe.db.get_value("Branch","Head Office","selco_collection_account")
            else:
                doc.paid_to = frappe.db.get_value("Branch",doc.selco_branch,"selco_collection_account")
        elif doc.mode_of_payment == "Cash":
            doc.paid_to = frappe.db.get_value("Branch",doc.selco_branch,"selco_collection_account_cash")
    elif doc.payment_type == "Pay":
        if doc.mode_of_payment == "Bank":
            doc.naming_series = frappe.db.get_value("Branch",doc.selco_branch,"selco_bank_payment_naming_series")
            doc.paid_from = frappe.db.get_value("Branch",doc.selco_branch,"selco_expenditure_account")

def selco_payment_entry_validate(doc,method):
    if doc.payment_type == "Receive":
        if doc.mode_of_payment == "Bank":
            doc.paid_to = frappe.db.get_value("Branch",doc.selco_branch,"selco_collection_account")
        elif doc.mode_of_payment == "Cash":
            doc.paid_to = frappe.db.get_value("Branch",doc.selco_branch,"selco_collection_account_cash")
            frappe.msgprint("Cash Account is" + doc.paid_to)
    local_sum = 0
    local_sum = doc.paid_amount
    for deduction in doc.deductions:
        local_sum = local_sum + deduction.amount
    doc.received_amount_with_deduction = local_sum

def selco_payment_entry_before_delete(doc,method):
    if "System Manager" not in frappe.get_roles():
        frappe.throw("You cannot delete Payment Entries")

def selco_journal_entry_before_insert(doc,method):
    frappe.msgprint(doc.name)
    local_cost_center = frappe.db.get_value("Branch",doc.selco_branch,"selco_cost_center")
    for account in doc.accounts:
        account.cost_center = local_cost_center

    if doc.voucher_type == "Contra Entry":
        doc.naming_series = frappe.db.get_value("Branch",doc.selco_branch,"selco_contra_naming_series")
    if doc.voucher_type == "Cash Payment":
        doc.naming_series = frappe.db.get_value("Branch",doc.selco_branch,"selco_cash_payment_naming_series")
    if doc.voucher_type == "Debit Note":
        doc.naming_series = frappe.db.get_value("Branch",doc.selco_branch,"selco_debit_note_naming_series")
    if doc.voucher_type == "Credit Note":
        doc.naming_series = frappe.db.get_value("Branch",doc.selco_branch,"selco_credit_note_naming_series")
    if doc.voucher_type == "Journal Entry":
        doc.naming_series = frappe.db.get_value("Branch",doc.selco_branch,"selco_journal_entry_naming_series")
    if doc.voucher_type == "Write Off Entry":
        doc.naming_series = frappe.db.get_value("Branch",doc.selco_branch,"selco_write_off_naming_series")
    if doc.voucher_type == "Bank Payment":
        doc.naming_series = frappe.db.get_value("Branch",doc.selco_branch,"selco_bank_payment_naming_series")
    if doc.voucher_type == "Receipt":
        doc.naming_series = frappe.db.get_value("Branch",doc.selco_branch,"selco_receipt_naming_series")
    if doc.voucher_type == "Commission Journal":
        doc.naming_series = frappe.db.get_value("Branch",doc.selco_branch,"selco_commission_journal_naming_series")
        # """if doc.branch == "Head Office" and doc.transfer_type == "Branch Collectiion To Platinum":
        #     doc.naming_series = frappe.db.get_value("Branch",doc.branch,"bank_payment_collection")
        # elif doc.branch == "Head Office" and doc.transfer_type == "Platinum To Branch Expenditure":
        #     doc.naming_series = frappe.db.get_value("Branch",doc.branch,"bank_payment_expenditure")"""

@frappe.whitelist()
def selco_journal_entry_validate(doc,method):
    local_cost_center = frappe.db.get_value("Branch",doc.selco_branch,"selco_cost_center")
    if doc.selco_use_different_cost_center == 1:
        local_cost_center = doc.selco_alternative_cost_center
    for account in doc.accounts:
        account.cost_center = local_cost_center

@frappe.whitelist()
def selco_purchase_invoice_before_insert(doc,method):
    if doc.is_return == 1:
        doc.naming_series = "DN/HO/16-17/"

    # BRANCH2WAREHOUSE
    # local_branch = frappe.db.get_value("Warehouse",doc.selco_godown,"selco_branch")
    # doc.naming_series = frappe.db.get_value("Branch",local_branch,"selco_purchase_invoice_naming_series")
    doc.naming_series = frappe.db.get_value("Warehouse", doc.selco_godown, "selco_purchase_invoice_naming_series")


@frappe.whitelist()
def selco_purchase_invoice_validate(doc,method):
    from erpnext.accounts.party import get_due_date
    doc.due_date = get_due_date(doc.selco_supplier_invoice_date,"Supplier",doc.supplier)
    #doc
    #doc.bill_no = doc.selco_supplier_invoice_number
    #doc.due_date = get_due_date(doc.selco_supplier_invoice_date, "Supplier", doc.supplier, doc.company)"

@frappe.whitelist()
def clean_up(doc,method):
    var1 = 1
    #var1 = frappe.get_doc("Purchase Receipt", "MRN/S/17/004")
    #var1.cancel()
    #frappe.delete_doc("Purchase Receipt", var1.name)
    #frappe.msgprint("Triggered")

@frappe.whitelist()
def selco_lead_before_insert(doc,method):
    doc.naming_series = frappe.db.get_value("Branch",doc.selco_branch,"selco_lead_naming_series")
    if doc.selco_project_enquiry == 1:
        doc.naming_series = "ENQ/17-18/"

@frappe.whitelist()
def selco_lead_validate(doc,method):
    if not ( doc.selco_customer_contact_number__mobile_1 or doc.selco_customer_contact_number__mobile_2_landline ):
        frappe.throw("Enter either Customer Contact Number ( Mobile 1 ) or Mobile 2 / Landline")
    if doc.selco_customer_contact_number__mobile_1 :
        if len(doc.selco_customer_contact_number__mobile_1 ) != 10:
            frappe.throw("Invalid Customer Contact Number ( Mobile 1 ) - Please enter exact 10 digits of mobile no ex : 9900038803")
        selco_validate_if_lead_contact_number_exists(doc.selco_customer_contact_number__mobile_1 ,doc.name)
    if doc.selco_customer_contact_number__mobile_2_landline:
        selco_validate_if_lead_contact_number_exists(doc.selco_customer_contact_number__mobile_2_landline,doc.name)


def selco_validate_if_lead_contact_number_exists(contact_number,lead_id):
    var4 = frappe.db.get_value("Lead", {"selco_customer_contact_number__mobile_2_landline": (contact_number)})
    var5 = unicode(var4) or u''
    var6 = frappe.db.get_value("Lead", {"selco_customer_contact_number__mobile_2_landline": (contact_number)}, "lead_name")
    if var5 != "None" and lead_id != var5:
        frappe.throw("Lead with contact no " + contact_number + " already exists \n Lead ID : " + var5 + "\n Lead Name : " + var6)

    var14 = frappe.db.get_value("Lead", {"selco_customer_contact_number__mobile_1": (contact_number)})
    var15 = unicode(var14) or u''
    var16 = frappe.db.get_value("Lead", {"selco_customer_contact_number__mobile_1": (contact_number)}, "lead_name")
    if var15 != "None" and lead_id != var15:
        frappe.throw("Lead with contact no " + contact_number + " already exists \n Lead ID : " + var15 + "\n Lead Name : " + var16)

# @frappe.whitelist()
def selco_address_before_insert(doc,method):
    pass
#     if doc.selco_customer_link:
#         temp_name = frappe.get_value("Customer",doc.selco_customer_link,"customer_name")
#         doc.address_title = doc.selco_customer_link + " - " + temp_name
#         doc.name = doc.selco_customer_link + " - " + temp_name + " - "
#     if doc.selco_customer_link:
#         doc.append("links",{"link_doctype":"Customer","link_name":doc.selco_customer_link})
#         #doc.links[0].link_name=doc.selco_customer_link


@frappe.whitelist()
def send_birthday_wishes():
    list_of_bday = frappe.db.sql('SELECT salutation,employee_name,designation,branch FROM `tabEmployee` where DAY(date_of_birth) = DAY(CURDATE()) AND MONTH(date_of_birth) = MONTH(CURDATE()) AND status="Active" ',as_list=True)
    bday_wish = ""
    if list_of_bday:
        for employee in list_of_bday:
            bday_wish += "<b> Dear " + employee[0] + "." + employee[1].upper() + " (" + employee[2] + "," + employee[3] +  ") " + "</b>" + "<br>"
        bday_wish += "<br>" + "सुदिनम् सुदिना जन्मदिनम् तव | भवतु मंगलं जन्मदिनम् || चिरंजीव कुरु कीर्तिवर्धनम् | चिरंजीव कुरुपुण्यावर्धनम् || विजयी भवतु सर्वत्र सर्वदा | जगति भवतु तव सुयशगानम् || <br><br>"
        bday_wish +="​ಸೂರ್ಯನಿಂದ ನಿಮ್ಮೆಡೆಗೆ ಬರುವ ಪ್ರತಿಯೊಂದು ರಶ್ಮಿಯೂ ನಿಮ್ಮ ಬಾಳಿನ ಸಂತಸದ ಕ್ಷಣವಾಗಲಿ ಎಂದು ಹಾರೈಸುತ್ತಾ ಜನುಮ ದಿನದ  ಹಾರ್ದಿಕ ​ಶುಭಾಶಯಗಳು​.​<br><br>"
        bday_wish +="Wishing you a wonderful day on your birthday. Let this be sacred and auspicious day for you. Wish you long live with a good fame and wish you long live with your good deeds. Wish you always make ever great achievements and let the world praise you for your success. Happy Birthday to our most beloved​. ​ ​SELCO Family wishes you Happy birthday.........!!!!!​​​ <br><br>"
        bday_wish +="Best Regards<br>"
        bday_wish +="SELCO Family​​<br>"
        local_recipient = []
        local_recipient.append("venugopal@selco-india.com")
        local_recipient.append("hr@selco-india.com")
        frappe.sendmail(
            recipients = local_recipient,
            subject="ಹುಟ್ಟುಹಬ್ಬದ ಶುಭಾಶಯಗಳು...............!!! - ERP",
            message=bday_wish)

@frappe.whitelist()
def send_po_reminder():
    list_of_po = frappe.db.sql('SELECT name FROM `tabPurchase Order` where workflow_state = "AGM Approval Pending - PO" ',as_list=True)
    po_reminder = "Please note below mentioned POs are in <b>AGM Approval Pending Status</b>, Please approve the same.<br/>"
    if list_of_po:
        for name in list_of_po:
            po_reminder += name[0]
            po_reminder += '<br/>'
        local_recipient = []
        local_recipient.append("jpai@selco-india.com")
        frappe.sendmail(
            recipients = local_recipient,
            subject="Purchase Order Approval Pending",
            message=po_reminder)

@frappe.whitelist()
def selco_stock_entry_on_submit_updates(doc,method):
    if((doc.selco_type_of_stock_entry == "Rejection Out") and (doc.selco_supplier_or_customer == "Customer")):
        for item in doc.items:
            ref_doc = frappe.get_doc("Stock Entry",item.reference_rej_in_or_rej_ot)
            #frappe.msgprint(ref_doc)
            for ref_item in ref_doc.items:
                if ref_item.item_code == item.item_code:
                    ref_item.reference_rej_in_or_rej_quantity = cint(ref_item.reference_rej_in_or_rej_quantity) + cint(item.qty)
                    if ref_item.reference_rej_in_or_rej_quantity > ref_item.qty:
                        frappe.throw("Please enter correct Quantity")
            ref_doc.save()
    if((doc.selco_type_of_stock_entry == "Rejection In") and (doc.selco_supplier_or_customer == "Supplier")):
        for item in doc.items:
            ref_doc = frappe.get_doc("Stock Entry",item.reference_rej_in_or_rej_ot)
            #frappe.msgprint(ref_doc)
            for ref_item in ref_doc.items:
                if ref_item.item_code == item.item_code:
                    ref_item.reference_rej_in_or_rej_quantity = cint(ref_item.reference_rej_in_or_rej_quantity) + cint(item.qty)
                    if ref_item.reference_rej_in_or_rej_quantity > ref_item.qty:
                        frappe.throw("Please enter correct Quantity")
            ref_doc.save(ignore_permissions=True)
    if(doc.selco_type_of_stock_entry == "GRN"):
        for item in doc.items:
            item.reference_rej_in_or_rej_ot = doc.selco_suppliers_ref
            ref_doc = frappe.get_doc("Stock Entry",doc.selco_suppliers_ref)
            #frappe.msgprint(ref_doc)
            for ref_item in ref_doc.items:
                if (ref_item.item_code == item.item_code and ref_item.item_code == item.item_code):
                    ref_item.reference_rej_in_or_rej_quantity = cint(ref_item.reference_rej_in_or_rej_quantity) + cint(item.qty)
                    if ref_item.reference_rej_in_or_rej_quantity > ref_item.qty:
                        frappe.throw("Please enter correct Quantity")
            ref_doc.save(ignore_permissions=True)
    if(doc.selco_type_of_stock_entry == "Outward DC"):
        pass
        """recipient_email_id  = frappe.db.get_value("Branch",doc.selco_being_dispatched_to,"selco_branch_email_id")
        dc_submitted = "Please note new outwrad DC <b>" + doc.name + " </b>has been submitted <br/>"
        frappe.sendmail(
            recipients = recipient_email_id,
            subject="Materials Dispatched To Your Branch",
            message=dc_submitted)"""

@frappe.whitelist()
def selco_stock_entry_on_cancel_updates(doc,method):
    if(doc.selco_type_of_stock_entry == "Rejection Out"):
        for item in doc.items:
            ref_doc = frappe.get_doc("Stock Entry",item.reference_rej_in_or_rej_ot)
            for ref_item in ref_doc.items:
                if ref_item.item_code == item.item_code:
                    ref_item.reference_rej_in_or_rej_quantity = cint(ref_item.reference_rej_in_or_rej_quantity) - cint(item.qty)
            ref_doc.save()
    """if(doc.type_of_stock_entry == "Rejection In"):
        for item in doc.items:
            ref_doc = frappe.get_doc("Stock Entry",item.reference_rej_in_or_rej_ot)
            for ref_item in ref_doc.items:
                if ref_item.item_code == item.item_code:
                    ref_item.reference_rej_in_or_rej_quantity = ref_item.reference_rej_in_or_rej_quantity - item.qty
            ref_doc.save()"""
    if(doc.selco_type_of_stock_entry == "GRN"):
        for item in doc.items:
            ref_doc = frappe.get_doc("Stock Entry",item.reference_rej_in_or_rej_ot)
            for ref_item in ref_doc.items:
                if ref_item.item_code == item.item_code:
                    ref_item.reference_rej_in_or_rej_quantity = cint(ref_item.reference_rej_in_or_rej_quantity) - cint(item.qty)
            ref_doc.save()

"""@frappe.whitelist()
def cleanup_si():
    for d in frappe.db.get_all("Sales Invoice",filters={"type_of_invoice": "Spare Sales Invoice"}):
        si = frappe.get_doc("Sales Invoice",d.name)
        si.cancel()
        si.delete()
    for d in frappe.db.get_all("Sales Invoice",filters={"type_of_invoice": "System Sales Invoice"}):
        si = frappe.get_doc("Sales Invoice",d.name)
        si.cancel()
        si.delete()
    for d in frappe.db.get_all("Sales Invoice",filters={"type_of_invoice": "Service Bill"}):
        si = frappe.get_doc("Sales Invoice",d.name)
        si.cancel()
        si.delete()
def cleanup_dc():
    for d in frappe.db.get_all("Delivery Note",filters={"docstatus": 2 }):
        dc = frappe.get_doc("Delivery Note",d.name)
        dc.delete()
    for d in frappe.db.get_all("Delivery Note",filters={"docstatus": 0 }):
        dc = frappe.get_doc("Delivery Note",d.name)
        dc.delete()
    for d in frappe.db.get_all("Delivery Note"):
        dc = frappe.get_doc("Delivery Note",d.name)
        dc.cancel()
        dc.delete()
def cleanup_se():
    for d in frappe.db.get_all("Stock Entry",filters={"docstatus": 0 }):
        dc = frappe.get_doc("Stock Entry",d.name)
        dc.delete()
    se_list = frappe.db.sql("select name from `tabStock Entry` where NULLIF(amended_from, '') IS NOT NULL AND docstatus AND  purpose = 'Material Transfer' ",as_list = True)
    for d in se_list:
        dc = frappe.get_doc("Stock Entry",d[0])
        dc.cancel()
        dc.delete()"""
@frappe.whitelist()
def selco_create_customer(selco_branch,customer_group,customer_name,selco_customer_contact_number,selco_landline_mobile_2,selco_gender,selco_electrification_status):
    local_cust = frappe.new_doc("Customer")
    local_cust.selco_branch = selco_branch
    local_cust.customer_group = customer_group
    local_cust.customer_name = customer_name
    local_cust.selco_customer_contact_number = selco_customer_contact_number
    local_cust.selco_landline_mobile_2 = selco_landline_mobile_2
    local_cust.selco_gender = selco_gender
    local_cust.selco_electrification_status = selco_electrification_status
    local_cust.insert()
    return local_cust.name,local_cust.customer_name
@frappe.whitelist()
def selco_add_new_address(selco_branch,address_type,address_line1,address_line2,city,selco_district,country,customer,address_title):
    from frappe.contacts.doctype.address.address import get_address_display
    local_address = frappe.new_doc("Address")
    local_address.selco_branch = selco_branch
    local_address.address_type = address_type
    local_address.address_line1 = address_line1
    local_address_line2 = address_line2
    local_address.city = city
    local_address.selco_district = selco_district
    local_address.country = country
    local_address.customer = customer

    local_address.address_title= address_title
    local_address.insert()
    return local_address.name,str(get_address_display(local_address.name))

@frappe.whitelist()
def selco_purchase_receipt_cancel_updates():
    from erpnext.buying.doctype.purchase_order.purchase_order import update_status
    mrn_list = frappe.db.sql("""SELECT name FROM `tabPurchase Receipt` where posting_date < '2016-06-11' """,as_list=True)
    for mrn in mrn_list:
        local_mrn = frappe.get_doc("Purchase Receipt",mrn[0])
        closed_po = []
        if local_mrn.status == "To Bill":
            for item in local_mrn.items:
                local_po1 = frappe.get_doc("Purchase Order",item.purchase_order)
                if local_po1.status == "Closed":
                    closed_po.append(local_po1.name)
                    update_status('To Receive and Bill',local_po1.name)
                    #local_po1.status = "To Receive and Bill"
                    #local_po1.save()
            local_mrn.cancel()
        for po in closed_po:
            update_status('Closed',po)
@frappe.whitelist()
def selco_stock_entry_cancel_updates():
    dc_list = frappe.db.sql("""SELECT name FROM `tabStock Entry` where posting_date BETWEEN '2017-10-01' AND '2017-10-02' ORDER BY posting_date DESC """,as_list=True)
    for dc in dc_list:
        local_dc = frappe.get_doc("Stock Entry",dc[0])
        if local_dc.docstatus == 1:
            local_dc.cancel()

@frappe.whitelist()
def selco_test_print():
    #my_attachments = [frappe.attach_print("Purchase Order", "PO/MPL/16-17/00468", file_name="po_file",print_format="SELCO PO")]
    my_attachments = []
    local_var = []
    receipt_list = frappe.db.sql("""SELECT name from `tabPayment Entry` where posting_date BETWEEN "20170901" AND "20170930" """,as_dict=True)
    for receipt in receipt_list:
        local_var += frappe.attach_print("Payment Entry", receipt, file_name="Receipts",print_format="SELCO_Receipt_4_Copies")
    my_attachments = local_var
    frappe.sendmail(
            recipients = ["basawaraj@selco-india.com"],
            subject="Your PO",
            message="PO",
            attachments=my_attachments,
            now=True)

@frappe.whitelist()
def get_default_address_name_and_display(doctype, docname):
    from frappe.contacts.doctype.address.address import get_address_display, get_default_address

    out = frappe._dict({"address_name": None, "address_display": None})
    default_address = get_default_address(doctype, docname)

    if default_address:
        out.address_name = default_address
        out.address_display = get_address_display(default_address)

    return out

