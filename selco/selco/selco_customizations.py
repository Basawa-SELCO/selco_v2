# -*- coding: utf-8 -*-
# Copyright (c) 2015, Selco and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe, json
from frappe import _
from frappe.model.document import Document
from frappe.utils import now,now_datetime, get_link_to_form, round_based_on_smallest_currency_fraction
import operator
from erpnext.accounts.party import get_party_account, get_due_date
from datetime import datetime
from datetime import timedelta
from frappe.utils import cint, getdate, add_days, add_months, date_diff, today
from erpnext.hr.doctype.employee.employee import get_holiday_list_for_employee

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
            if frappe.get_cached_value("Service Person",info[i][32],"send_sms") :
                cn=str(frappe.get_cached_value("Service Person",info[i][32],"contact_number"))+"@sms.textlocal.in"
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
    doc.naming_series = frappe.get_cached_value("Branch",doc.selco_branch,"selco_customer_complaint_naming_series")

@frappe.whitelist()
def selco_warranty_claim_validate(doc,method):
    service_manager_email_id, godown_email_id = frappe.get_cached_value("Branch",
        doc.selco_branch, ["selco_service_manager_email_id", "selco_godown_email_id"])

    doc.selco_senior_service_manager_email_id = service_manager_email_id
    doc.selco_godown_email_id = godown_email_id
    set_issue_workslow(doc)

def set_issue_workslow(doc):
	workflow_dict = {
		'Warranty Claim Format Raised - WC': 'Warranty Claim Format Raised - WC',
		'Warranty Claim Approved - WC': 'Dispatch Pending From Godown',
		'Warranty Claim Rejected - WC': 'Complaint Attended By CSE - Still Open',
		'Dispatched From Godown': 'Dispatched From Godown'
	}

	if doc.selco_complaint_number:
		if doc.workflow_state in workflow_dict:
			frappe.db.set_value('Issue', doc.selco_complaint_number,
				'workflow_state', workflow_dict.get(doc.workflow_state))

@frappe.whitelist()
def selco_get_items_from_rejection_in_or_out(stock_entry, branch):
	doc = frappe.get_doc('Stock Entry', stock_entry)

	items = []
	for d in doc.items:
		items.append({
			's_warehouse': d.t_warehouse,
			'item_code': d.item_code,
			'item_name': d.item_name,
			'transfer_qty':d.transfer_qty,
			'description': d.description,
			'qty': d.qty,
			'uom': d.uom,
			'item_group': d.item_group,
			'basic_rate': d.basic_rate,
			'against_stock_entry': d.parent,
			'ste_detail': d.name,
			'stock_uom': d.stock_uom,
			'conversion_factor': d.conversion_factor,
			'serial_no': d.serial_no,
			'batch_no': d.batch_no
		})
	
	return items

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
def selco_delivery_note_validates(doc,method):
    selco_warehouse, selco_cost_center = frappe.get_cached_value("Branch",
        doc.selco_branch, ["selco_warehouse", "selco_cost_center"])

    for d in doc.get('items'):
        d.warehouse = selco_warehouse
        d.cost_center = selco_cost_center
        if not d.rate:
            d.rate = frappe.get_cached_value("Item Price",
                {"price_list": "Branch Sales", "item_code":d.item_code}, "price_list_rate")

@frappe.whitelist()
def selco_delivery_note_before_insert(doc,method):
    if doc.is_return:
        doc.naming_series = "DC-RET/"
    else:
        doc.naming_series = frappe.get_cached_value("Branch",
            doc.selco_branch, "selco_delivery_note_naming_series")

    selco_warehouse, selco_cost_center = frappe.get_cached_value("Branch",
        doc.selco_branch, ["selco_warehouse", "selco_cost_center"])

    for d in doc.get('items'):
        d.warehouse = selco_warehouse
        d.cost_center = selco_cost_center
        if not d.rate:
            d.rate = frappe.get_cached_value("Item Price",
                {"price_list": "Branch Sales", "item_code":d.item_code}, "price_list_rate")

@frappe.whitelist()
def selco_material_request_before_insert(doc,method):
    doc.naming_series = frappe.get_cached_value("Branch",doc.selco_branch,"selco_material_request_naming_series")
    local_warehouse = frappe.get_cached_value("Branch",doc.selco_branch,"selco_git_warehouse")
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
                d.selco_dispatched_quantity = d.qty

    if doc.workflow_state == "Dispatched From Godown - IBM":
        for d in doc.get('items'):
            d.selco_dispatched_quantity = d.qty

    data = frappe.get_cached_value("Branch", doc.selco_branch,
        ["selco_branch_credit_limit", "selco_senior_sales_manager_email_id",
        "selco_godown_email_id", "selco_agm_email_id"], as_dict=1)

    if data:
        doc.selco_branch_credit_limit = data.selco_branch_credit_limit
        doc.selco_senior_sales_manager_email_id = data.selco_senior_sales_manager_email_id
        doc.selco_godown_email_id = data.selco_godown_email_id
        doc.selco_agms_email_id = data.selco_agm_email_id

@frappe.whitelist()
def selco_material_approved_and_dispatched(doc,method):
    #frappe.msgprint("selco_material_approved_and_dispatched")

    if doc.workflow_state == "Approved - IBM":
         doc.selco_approved_time = now()

    elif doc.workflow_state == "Dispatched From Godown - IBM":
        doc.selco_dispatched_time = now()

@frappe.whitelist()
def selco_purchase_receipt_before_insert(doc,method):
    if doc.is_return == 1:
        doc.naming_series = frappe.db.get_value("Warehouse", doc.selco_godown, "selco_purchase_receipt_return_naming_series")
    else:
        doc.naming_series = frappe.get_cached_value("Warehouse",
            doc.selco_godown, "selco_mrn_naming_series")

@frappe.whitelist()
def selco_purchase_order_before_insert(doc,method):
    doc.naming_series = frappe.get_cached_value("Warehouse",
        doc.selco_godown, "selco_po_naming_series")

@frappe.whitelist()
def selco_purchase_order_validate(doc,method):
    if doc.selco_godown:
        godown_address_ret = get_default_address_name_and_display("Warehouse", doc.selco_godown)
        doc.selco_godown_address = godown_address_ret.address_name
        doc.selco_godown_address_details = godown_address_ret.address_display

    doc.selco_godown_email = frappe.get_cached_value("Warehouse",doc.selco_godown,"selco_godown_email")

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
    # local_branch = frappe.get_cached_value("Warehouse",doc.selco_godown,"selco_branch")
    # selco_cost_center = frappe.get_cached_value("Branch",local_branch,"selco_cost_center")
    godown_cost_center = frappe.get_cached_value("Warehouse", doc.selco_godown, "selco_cost_center")

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
        if item_selco.purchase_order and item_selco.purchase_order not in po_list:
            po_list.append(item_selco.purchase_order)
            po_list_date.append(frappe.utils.formatdate(frappe.get_cached_value('Purchase Order', item_selco.purchase_order, 'transaction_date'),"dd-MM-yyyy"))
    doc.selco_list_of_po= ','.join([str(i) for i in po_list])
    doc.selco_list_of_po_date= ','.join([str(i) for i in po_list_date])
    #End of Insert By basawaraj On 7th september for printing the list of PO when PR is done by importing items from multiple PO
    if doc.selco_type_of_purchase == "Normal":
        for d in doc.get('items'):
            if not d.purchase_order :
                frappe.throw("Purchase Order Is Mandatory")

def selco_stock_entry_updates(doc,method):
    if not doc.selco_branch and doc.get("items"):
        warehouse = doc.items[0].s_warehouse
        doc.selco_branch = frappe.db.get_value("Branch", {"selco_warehouse": warehouse}, "name")

    if not doc.selco_branch:
        frappe.throw(_("Select branch for stock entry {0}").format(doc.name))

    branch_data = frappe.get_cached_value("Branch", doc.selco_branch,
        ['supplier_replaceable', 'defective_warehouse', 'selco_cost_center', 'selco_warehouse', 'selco_repair_warehouse', 
            'selco_receipt_note_naming_series','selco_stock_entry_naming_series', 'selco_rejection_in_naming_series', 
            'selco_rejection_out_naming_series', 'selco_bill_of_material_naming_series', 'selco_other_stock_entry_naming_series'], as_dict=1)

    for label in ["Cost Center", "Warehouse", "Repair Warehouse"]:
        field = 'selco_{0}'.format(frappe.scrub(label))
        if not branch_data.get(field):
            frappe.throw(_("Please set {0} in the selected Branch {1}")
                .format(label, doc.selco_branch))

    if doc.stock_entry_type in ['Outward DC', 'GRN']:
        if doc.is_new():
            doc.naming_series = (branch_data.selco_receipt_note_naming_series
                if doc.purpose=="Receive at Warehouse" else branch_data.selco_stock_entry_naming_series)

        warehouse = (branch_data.selco_warehouse
            if doc.selco_type_of_material=="Good Stock" else branch_data.selco_repair_warehouse)

        if doc.selco_type_of_material in ["Defective", "Supplier Replaceable"]:
            warehouse = (branch_data.defective_warehouse
                if doc.selco_type_of_material=="Defective" else branch_data.supplier_replaceable)

        git_warehouse = frappe.get_cached_value("Branch",
            doc.selco_branch, 'selco_git_warehouse')

        if doc.selco_being_dispatched_to:
            branch_selco_being_dispatched_to = doc.selco_being_dispatched_to

            if doc.selco_type_of_material in ["Good Stock", "Repair Stock"]:
                git_warehouse = frappe.get_cached_value("Branch",
                    branch_selco_being_dispatched_to, 'selco_git_warehouse' if doc.selco_type_of_material=="Good Stock" else 'repair_git_warehouse')

            else:
                git_warehouse = frappe.get_cached_value("Branch",
                    branch_selco_being_dispatched_to, 'common_git')

        for d in doc.get('items'):
            d.cost_center = branch_data.selco_cost_center
            d.s_warehouse = (git_warehouse
                if doc.purpose=="Receive at Warehouse" else warehouse)

            d.t_warehouse = (warehouse
                if doc.purpose=="Receive at Warehouse" else git_warehouse)

        if doc.selco_type_of_material != "Good Stock" and git_warehouse != "Demo Warehouse - SELCO":
                d.is_sample_item = 1

    elif doc.stock_entry_type in ["Rejection In", "Rejection Out"]:
        if doc.is_new():
            doc.naming_series = (branch_data.selco_rejection_in_naming_series
                if doc.purpose == 'Material Receipt' else branch_data.selco_rejection_out_naming_series)

        warehouse_field = "t_warehouse" if doc.purpose == 'Material Receipt' else "s_warehouse"

        for d in doc.get('items'):
            d.cost_center = branch_data.selco_cost_center
            d.set(warehouse_field, branch_data.selco_repair_warehouse)
            d.is_sample_item = 1

    elif doc.is_new() and doc.stock_entry_type == "BOM":
        doc.naming_series = branch_data.selco_bill_of_material_naming_series

    elif doc.is_new():
        doc.naming_series = branch_data.selco_other_stock_entry_naming_series

    if doc.stock_entry_type == "BOM":
        total_count = len(doc.items)
        for row in doc.items:
            row.s_warehouse = ''
            row.t_warehouse = ''

            row.cost_center = branch_data.selco_cost_center
            if row.idx == total_count:
                row.t_warehouse = branch_data.selco_warehouse
            else:
                row.s_warehouse = branch_data.selco_warehouse

    if doc.purpose == "Send to Warehouse":
        doc.selco_recipient_email_id = frappe.get_cached_value("Branch",doc.selco_being_dispatched_to,"selco_branch_email_id")

@frappe.whitelist()
def selco_stock_entry_validate(doc,method):
    from frappe.contacts.doctype.address.address import get_address_display, get_default_address
    if doc.purpose == "Send to Warehouse":
        local_warehouse = frappe.get_cached_value("Branch",doc.selco_being_dispatched_to,"selco_warehouse")
        doc.selco_recipient_address_link = get_default_address("Warehouse", local_warehouse) #frappe.get_cached_value("Warehouse",local_warehouse,"address")
        doc.selco_recipient_address = "<b>" + doc.selco_being_dispatched_to.upper() + " BRANCH</b><br>"
        doc.selco_recipient_address+= "SELCO SOLAR LIGHT PVT. LTD.<br>"
        doc.selco_recipient_address+= str(get_address_display(doc.selco_recipient_address_link))
    elif doc.purpose=="Receive at Warehouse":
        sender = frappe.get_cached_value("Stock Entry",doc.outgoing_stock_entry,"selco_branch")
        sender_warehouse = frappe.get_cached_value("Branch",sender,"selco_warehouse")
        doc.sender_address_link = get_default_address("Warehouse", sender_warehouse) #frappe.get_cached_value("Warehouse",sender_warehouse,"address")
        doc.sender_address = "<b>" + str(sender) + " SELCO BRANCH</b><br>"
        doc.sender_address += "SELCO SOLAR LIGHT PVT. LTD.<br>"
        doc.sender_address += str(get_address_display(doc.sender_address_link))

        if frappe.get_cached_value("Stock Entry",doc.outgoing_stock_entry,"purpose") != 'Send to Warehouse':
            frappe.throw(_("Stock Entry (Outward GIT) should be outward dc."))

@frappe.whitelist()
def get_items_from_outward_stock_entry(selco_doc_num,selco_branch):
    selco_var_dc = frappe.get_doc("Stock Entry",selco_doc_num)
    if selco_var_dc.selco_type_of_stock_entry != "Demo - Material Issue" and selco_var_dc.selco_being_dispatched_to != selco_branch:
        frappe.throw("Incorrect DC Number");
    from_warehouse = selco_var_dc.to_warehouse
    if selco_var_dc.selco_type_of_material=="Good Stock":
        to_warehouse = frappe.get_cached_value("Branch",selco_var_dc.selco_being_dispatched_to,"selco_warehouse")
    else:
        to_warehouse = frappe.get_cached_value("Branch",selco_var_dc.selco_being_dispatched_to,"selco_repair_warehouse")
    return { 'dc' : selco_var_dc,'from_warehouse' : from_warehouse, 'to_warehouse' :to_warehouse }

@frappe.whitelist()
def get_items_from_rejection_in(selco_rej_in,selco_branch):
    selco_var_dc = frappe.get_doc("Stock Entry",selco_rej_in)
    return { 'dc' : selco_var_dc }

@frappe.whitelist()
def selco_customer_before_insert(doc, method):
    doc.naming_series = frappe.get_cached_value("Branch",
        doc.selco_branch, "selco_customer_naming_series")

@frappe.whitelist()
def selco_customer_validate(doc,method):
    if not ( doc.selco_customer_contact_number or doc.selco_landline_mobile_2 ):
        frappe.throw("Enter either Customer Contact Number ( Mobile 1 ) or Mobile 2 / Landline")
    if doc.selco_customer_contact_number:
        if len(doc.selco_customer_contact_number) != 10:
            frappe.throw("Invalid Customer Contact Number ( Mobile 1 ) - Please enter exact 10 digits of mobile no ex : 9900038803")
        selco_validate_if_customer_contact_number_exists(doc.selco_customer_contact_number,doc.name)
    if doc.selco_landline_mobile_2:
        selco_validate_if_customer_contact_number_exists(doc.selco_landline_mobile_2,doc.name)

def selco_validate_if_customer_contact_number_exists(contact_number,customer_id):
	for field in ["selco_customer_contact_number", "selco_landline_mobile_2"]:
		duplicate_customer = frappe.db.get_value("Customer", 
			{field: contact_number, "name": ("!=", customer_id)}, "name")

		if duplicate_customer:
			frappe.throw(_("Same contact no {0} already exists for the customer {1}")
				.format(contact_number, duplicate_customer))

@frappe.whitelist()
def selco_sales_invoice_before_insert(doc,method):
    selco_cost_center = frappe.get_cached_value("Branch", doc.selco_branch, "selco_cost_center")
    for d in doc.get('items'):
        d.cost_center = selco_cost_center
        d.income_account = doc.selco_sales_account

    for d in doc.get('taxes'):
        d.cost_center = selco_cost_center

    customer_data = frappe.get_cached_value("Customer",
        doc.customer, ["selco_customer_contact_number", "selco_customer_tin_number"], as_dict=1)

    doc.selco_customer_contact_number = customer_data.get("selco_customer_contact_number")
    doc.selco_customer_tin_number = customer_data.get("selco_customer_tin_number")
    if doc.is_return == 1:
        doc.naming_series = frappe.get_cached_value("Branch",doc.selco_branch,"selco_credit_note_naming_series")
    else:
        if doc.selco_type_of_invoice in ["System Sales Invoice", "Spare Sales Invoice"]:
            doc.naming_series = frappe.get_cached_value("Branch",doc.selco_branch,"selco_sales_invoice_naming_series")
        elif doc.selco_type_of_invoice == "Write Off":
            doc.naming_series = frappe.get_cached_value("Branch",doc.selco_branch,"selco_write_off_naming_series")
        elif doc.selco_type_of_invoice == "Service Bill":
            doc.naming_series = frappe.get_cached_value("Branch",doc.selco_branch,"selco_service_bill_naming_series")
        elif doc.selco_type_of_invoice == "Bill of Sale":
            doc.naming_series = frappe.get_cached_value("Branch",doc.selco_branch,"selco_bill_of_sales_naming_series")


def selco_sales_invoice_cancel(doc, method=None):
	delete_auto_created_maintenance_schedule(doc)

def delete_auto_created_maintenance_schedule(doc):
	for row in frappe.get_all("Maintenance Schedule", filters={"docstatus": 0, "sales_invoice": doc.name}):
		frappe.delete_doc("Maintenance Schedule", row.name)

def selco_sales_invoice_submit(doc, method):
	make_maintenance_schedule(doc)

def make_maintenance_schedule(doc):
	if doc.is_return:
		if doc.return_against:
			for d in frappe.get_all('Maintenance Schedule', 
				filters={'sales_invoice': doc.return_against, 'docstatus': 0}):
				frappe.delete_doc("Maintenance Schedule", d.name)

		return

	ms_doc = frappe.get_cached_doc("Maintenance Settings", "Maintenance Settings")
	if (ms_doc.auto_create_maintenance_schedule and doc.start_date
		and doc.end_date and doc.periodicity and (doc.selco_type_of_invoice == "System Sales Invoice" or
		ms_doc.role_to_make_maintenance_schedule in frappe.get_roles(frappe.session.user))):
		schedule_list = create_schedule_list(doc.start_date,
			doc.end_date, doc.no_of_visits, doc)

		days_diff = 0
		for i, from_date in enumerate(schedule_list):
			m_doc = frappe.get_doc({
				'doctype': 'Maintenance Schedule',
                                'company': doc.company,
				'customer': doc.customer,
				'transaction_date': from_date,
				'sales_invoice': doc.name,
				'customer_address': doc.shipping_address_name or doc.customer_address,
				'address_display': doc.shipping_address or doc.address_display,
				'naming_series': frappe.get_cached_value("Branch",
					doc.selco_branch, "selco_maintenance_schedule_naming_series")
			})

			end_date = from_date
			start_date = add_days(from_date, -1)

			for d in doc.items:
				m_doc.append('items', {
					'item_code': d.item_code,
					'item_name': d.item_name,
					'description': d.description,
					'start_date': start_date,
					'end_date':end_date,
					'no_of_visits': 1,
					'service_person': doc.service_person,
					'sales_person': doc.sales_team[0].sales_person
				})

			m_doc.generate_schedule()
			m_doc.selco_branch = doc.selco_branch
			m_doc.save()
			frappe.msgprint(_("Maintenance Schedule {0} created").format(get_link_to_form("Maintenance Schedule", m_doc.name)))

def create_schedule_list(start_date, end_date, no_of_visit, doc):
		schedule_list = []
		start_date_copy = start_date
		date_diff = (getdate(end_date) - getdate(start_date)).days
		add_by = date_diff / no_of_visit

		for visit in range(cint(no_of_visit)):
			if (getdate(start_date_copy) <= getdate(end_date)):
				start_date_copy = add_days(start_date_copy, add_by)
				if len(schedule_list) < no_of_visit:
					schedule_date = validate_schedule_date_for_holiday_list(getdate(start_date_copy), doc.service_person, doc.company)
					if schedule_date > getdate(end_date):
						schedule_date = getdate(end_date)
					schedule_list.append(schedule_date)

		return schedule_list

def validate_schedule_date_for_holiday_list(schedule_date, service_person, company):
		validated = False

		employee = frappe.db.get_value("Service Person", service_person, "employee")
		if employee:
			holiday_list = get_holiday_list_for_employee(employee)
		else:
			holiday_list = frappe.get_cached_value('Company',  company,  "default_holiday_list")

		holidays = frappe.db.sql_list('''select holiday_date from `tabHoliday` where parent=%s''', holiday_list)

		if not validated and holidays:

			# max iterations = len(holidays)
			for i in range(len(holidays)):
				if schedule_date in holidays:
					schedule_date = add_days(schedule_date, 1)
				else:
					validated = True
					break

		return schedule_date

@frappe.whitelist()
def selco_sales_invoice_validate(doc,method):
    #selco_warehouse  = frappe.get_cached_value("Branch",doc.branch,"selco_warehouse")
    selco_cost_center = frappe.get_cached_value("Branch", doc.selco_branch, "selco_cost_center")

    doc.total_sales_person_incentive, doc.total_budget_value = 0.0, 0.0
    doc.total_commission = 0.0

    for d in doc.get('taxes'):
        d.cost_center = selco_cost_center

    for i,c in enumerate(doc.get('taxes')):
        if doc.taxes[i].account_head == "Discount Karnataka 14.5% - SELCO":
           if doc.taxes[i].tax_amount>0:
              doc.taxes[i].tax_amount = doc.taxes[i].tax_amount * -1

    if doc.start_date and doc.periodicity:
        month_map = {'Monthly': 1, 'Quarterly': 3, 'Half Yearly': 6, 'Yearly': 12}
        mcount = month_map.get(doc.periodicity)
        if mcount:
            doc.end_date = add_months(doc.start_date, mcount * cint(doc.no_of_visits))
        else:
            days = 7 if doc.periodicity == 'Weekly' else 2
            doc.end_date = add_days(doc.start_date, days)

    no_commission = False
    if doc.selco_type_of_invoice not in ["System Sales Invoice", "Spare Sales Invoice", "Service Bill"]:
        no_commission = True

    if doc.selco_type_of_invoice == "Spare Sales Invoice" and doc.grand_total < 1000:
        no_commission = True

    if no_commission:
        for d in doc.get('items'):
            d.commission_rate_for_sales_person = 0.0
            d.commission_rate_for_sales_partner = 0.0
            d.commission_rate_for_budget = 0.0
            d.commission_value_of_sales_person = 0.0
            d.commission_value_of_sales_partner = 0.0
            d.value_of_budget = 0.0
        doc.total_sales_person_incentive = 0.0
        doc.total_budget_value = 0.0

        for row in doc.sales_team:
            row.budget = 0.0
            row.incentives = 0.0

        return

    # Check Commission Rate present in the sales partner or not, if not then check in the item group
    for d in doc.get('items'):
        commission_rate_for_sales_person = 0.0
        commission_rate_for_sales_partner = 0.0
        commission_rate_for_budget = 0.0

        if doc.sales_partner:
            budget_data = frappe.db.get_value("Sales Partner Budget", 
                    {"parent": doc.sales_partner, "item_group": d.item_group}, ["commission_rate_for_sales_person", 
                        "commission_rate_for_sales_partner", "commission_rate_for_budget"])

            if budget_data:
                commission_rate_for_sales_person = budget_data[0] or frappe.db.get_value("Item Group", d.item_group, "commission_rate_for_sales_person")
                commission_rate_for_sales_partner = budget_data[1] or frappe.db.get_value("Item Group", d.item_group, "commission_rate_for_sales_partner")
                commission_rate_for_budget = budget_data[2] or frappe.db.get_value("Item Group", d.item_group, "commission_rate_for_budget")

        if doc.selco_skdrdp_staff == "Yes":
            commission_rate_for_sales_partner = 0.0

        d.commission_rate_for_sales_person = commission_rate_for_sales_person or frappe.db.get_value("Item Group", d.item_group, "commission_rate_for_sales_person")

        d.commission_rate_for_sales_partner = commission_rate_for_sales_partner or frappe.db.get_value("Item Group", d.item_group, "commission_rate_for_sales_partner")

        d.commission_rate_for_budget = commission_rate_for_budget or frappe.db.get_value("Item Group", d.item_group, "commission_rate_for_budget")

        d.cost_center = selco_cost_center
        d.income_account = doc.selco_sales_account
        d.commission_value_of_sales_person = round_based_on_smallest_currency_fraction((d.net_amount * d.commission_rate_for_sales_person) / 100, doc.currency)
        d.commission_value_of_sales_partner = round_based_on_smallest_currency_fraction((d.net_amount * d.commission_rate_for_sales_partner) / 100, doc.currency)
        d.value_of_budget = round_based_on_smallest_currency_fraction((d.net_amount * d.commission_rate_for_budget) / 100, doc.currency)

        doc.total_sales_person_incentive += round_based_on_smallest_currency_fraction(d.commission_value_of_sales_person, doc.currency)
        doc.total_budget_value += round_based_on_smallest_currency_fraction(d.value_of_budget, doc.currency)
        doc.total_commission += round_based_on_smallest_currency_fraction(d.commission_value_of_sales_partner, doc.currency)

    for d in doc.sales_team:
        if doc.total_sales_person_incentive:
            d.incentives = (doc.total_sales_person_incentive * d.allocated_percentage) / 100

        if doc.total_budget_value:
            d.budget = (doc.total_budget_value * d.allocated_percentage) / 100

    if not doc.sales_partner and doc.total_commission:
        doc.total_commission = 0.0

def selco_payment_entry_before_insert(doc,method):
    if doc.payment_type == "Receive":
        data = frappe.get_cached_value("Branch", doc.selco_branch,
            ["selco_receipt_naming_series", "selco_collection_account"], as_dict=1)

        doc.naming_series = data.selco_receipt_naming_series
        doc.paid_to = data.selco_collection_account

        if (doc.mode_of_payment == "Bank"
            and doc.selco_amount_credited_to_platinum_account):
            doc.paid_to = frappe.get_cached_value("Branch","Head Office","selco_collection_account")

        elif doc.mode_of_payment == "Cash":
            doc.paid_to = frappe.db.get_value("Branch",doc.selco_branch,"selco_collection_account_cash")

    elif doc.payment_type == "Pay":
        if doc.mode_of_payment == "Bank":
            data = frappe.get_cached_value("Branch", doc.selco_branch,
                ["selco_bank_payment_naming_series", "selco_expenditure_account"], as_dict=1)

            doc.naming_series = data.selco_bank_payment_naming_series
            doc.paid_from = data.selco_expenditure_account

def selco_payment_entry_validate(doc,method):
    if doc.payment_type == "Receive":
        if doc.selco_money_received_by == "Cash":
            doc.mode_of_payment = "Cash"
            doc.paid_to = frappe.get_cached_value("Branch",doc.selco_branch,"selco_collection_account_cash")
        else:
            doc.mode_of_payment = "Bank"
            doc.paid_to = frappe.get_cached_value("Branch",doc.selco_branch,"selco_collection_account")

    local_sum = 0
    local_sum = doc.paid_amount

    for deduction in doc.deductions:
        local_sum = local_sum + deduction.amount

    doc.received_amount_with_deduction = local_sum

def selco_payment_entry_before_delete(doc,method):
    if "System Manager" not in frappe.get_roles():
        frappe.throw("You cannot delete Payment Entries")

def selco_journal_entry_before_insert(doc, method):
    if not doc.selco_branch:
        for d in doc.get("accounts"):
            if d.reference_type in ["Sales Invoice"]:
                doc.selco_branch = frappe.db.get_value(d.reference_type, d.reference_name, "selco_branch")

    naming_series_dict = {
        'Contra Entry': 'selco_contra_naming_series', 'Cash Entry': 'selco_cash_payment_naming_series',
        'Debit Note': 'selco_debit_note__naming_series', 'Credit Note': 'selco_credit_note_naming_series',
        'Journal Entry': 'selco_journal_entry_naming_series', 'Write Off Entry': 'selco_write_off_naming_series',
        'Bank Entry': 'selco_bank_payment_naming_series', 'Receipt': 'selco_receipt_naming_series',
        'Commission Journal': 'selco_commission_journal_naming_series'
    }

    naming_series_field = naming_series_dict.get(doc.voucher_type)
    if not naming_series_field: return

    data = frappe.get_cached_value("Branch",
        doc.selco_branch, ["selco_cost_center", naming_series_field], as_dict=1)

    doc.naming_series = data.get(naming_series_field)
    for account in doc.accounts:
        account.cost_center = data.selco_cost_center

@frappe.whitelist()
def selco_journal_entry_validate(doc,method):
    local_cost_center = frappe.get_cached_value("Branch",doc.selco_branch,"selco_cost_center")
    if doc.selco_use_different_cost_center == 1:
        local_cost_center = doc.selco_alternative_cost_center
    for account in doc.accounts:
        account.cost_center = local_cost_center

@frappe.whitelist()
def selco_purchase_invoice_before_insert(doc,method):
    if doc.is_return == 1:
        doc.naming_series = frappe.db.get_value("Warehouse",doc.selco_godown,"selco_purchase_invoice_return_naming_series")
    else:
        doc.naming_series = frappe.get_cached_value("Warehouse", doc.selco_godown, "selco_purchase_invoice_naming_series")


@frappe.whitelist()
def selco_purchase_invoice_validate(doc, method):
    from erpnext.accounts.party import get_due_date

    doc.due_date = get_due_date(doc.selco_supplier_invoice_date,"Supplier",doc.supplier)

@frappe.whitelist()
def selco_lead_before_insert(doc,method):
    doc.naming_series = frappe.get_cached_value("Branch",doc.selco_branch,"selco_lead_naming_series")
    if doc.selco_project_enquiry == 1:
        doc.naming_series = frappe.db.get_value("Branch",doc.selco_branch,"selco_project_enquiry_naming_series")

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

def stock_entry_reference_qty_update(doc, method):
    if doc.docstatus == 1 and doc.purpose == 'Send to Warehouse':
      make_stock_receive_entry(doc)

    itemwise_count_dict = {}
    if doc.stock_entry_type in ["Rejection In", "Rejection Out", "Outward DC", "GRN"]:
        for row in doc.items:
            itemwise_count_dict.setdefault(row.item_code, []).append(row.idx)

            if len(itemwise_count_dict[row.item_code]) > 1:
                frappe.throw(_("The item code {0} has been added multiple times").format(row.item_code))

    for item in doc.items:
        if (doc.stock_entry_type=="Receive at Warehouse" or doc.purpose=="Receive at Warehouse") and doc.outgoing_stock_entry:
            item.reference_rej_in_or_rej_ot = doc.outgoing_stock_entry
        elif doc.stock_entry_type=="Rejection Out" and doc.selco_rejection_in_id:
            item.reference_rej_in_or_rej_ot = doc.selco_rejection_in_id
        elif doc.stock_entry_type=="Rejection In" and doc.selco_rejection_out_id:
            item.reference_rej_in_or_rej_ot = doc.selco_rejection_out_id

        if item.reference_rej_in_or_rej_ot:
            data = frappe.get_all('Stock Entry Detail',
                fields = ["sum(qty) as qty"],
                filters = {'docstatus': 1, 'reference_rej_in_or_rej_ot': item.reference_rej_in_or_rej_ot,
                    'item_code': item.item_code})

            reference_qty = data[0].qty if data else 0

            name, ste_qty = frappe.db.get_value('Stock Entry Detail',
               {'parent': item.reference_rej_in_or_rej_ot,
                    'item_code': item.item_code}, ['name', 'qty'])

            if reference_qty and reference_qty > ste_qty:
                if doc.stock_entry_type=="Rejection In" and item.reference_rej_in_or_rej_ot:
                    frappe.throw(_("Row {0}: For the item {1}, already received the all quantity against the rejection out {2}")
                        .format(item.idx, frappe.bold(item.item_code), get_link_to_form("Stock Entry", item.reference_rej_in_or_rej_ot)))

                else:
                    if doc.stock_entry_type=="Rejection Out":
                        frappe.throw(_("Row {0}: For the item {1}, already outward the all quantity against the rejection in {2}")
                            .format(item.idx, frappe.bold(item.item_code), get_link_to_form("Stock Entry", item.reference_rej_in_or_rej_ot)))
                    if doc.stock_entry_type == "GRN":
                        frappe.throw(_("Row {0}: For the item {1}, the GRN quantity is more than the outward dc quantity in {2}")
                            .format(item.idx, frappe.bold(item.item_code), get_link_to_form("Stock Entry", item.reference_rej_in_or_rej_ot)))

            frappe.db.set_value('Stock Entry Detail', name,
                'reference_rej_in_or_rej_quantity', reference_qty)

def make_stock_receive_entry(doc):
	from erpnext.stock.doctype.stock_entry.stock_entry import make_stock_in_entry

	new_doc = make_stock_in_entry(doc.name)
	new_doc.selco_branch = doc.selco_being_dispatched_to
	new_doc.purpose = 'Receive at Warehouse'
	new_doc.set_stock_entry_type()
	selco_stock_entry_updates(new_doc, '')
	new_doc.save(ignore_permissions=True)
	frappe.msgprint(_("Receive at warehouse entry {0} created").format(new_doc.name))

@frappe.whitelist()
def get_stock_entry(doctype, txt, searchfield, start, page_len, filters):
    cond = "1=1"
    if filters.get('selco_supplier_or_customer'):
        cond = """se.selco_supplier_or_customer_id = %(selco_supplier_or_customer_id)s
            and se.selco_type_of_stock_entry = %(selco_type_of_stock_entry)s"""
    elif filters.get('selco_type_of_stock_entry') == 'GRN':
        cond = """se.selco_type_of_stock_entry = 'Outward DC'
            and se.selco_inward_or_outward = 'Outward'
            and se.selco_being_dispatched_to = %(selco_branch)s """

    return frappe.db.sql(""" SELECT distinct sed.parent
        FROM
            `tabStock Entry Detail` sed,
            `tabStock Entry` se
        WHERE
            se.name = sed.parent and se.docstatus = 1 and
            ifnull(reference_rej_in_or_rej_quantity, 0) < qty and
            sed.parent like %(txt)s and se.name != %(name)s and {cond}
        LIMIT %(start)s, %(page_len)s """.format(cond = cond), {
            'txt': '%' + txt + '%',
            "name": filters.get("name"),
			"start": start, "page_len": page_len,
            "selco_supplier_or_customer_id": filters.get('selco_supplier_or_customer_id'),
            "selco_type_of_stock_entry": filters.get("selco_type_of_stock_entry"),
            "selco_branch": filters.get("selco_branch")
        })

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
def get_default_address_name_and_display(doctype, docname):
    from frappe.contacts.doctype.address.address import get_address_display, get_default_address

    if doctype and docname:
        out = frappe._dict({"address_name": None, "address_display": None})
        default_address = get_default_address(doctype, docname)

        if default_address:
            out.address_name = default_address
            out.address_display = get_address_display(default_address)

        return out

@frappe.whitelist()
def get_incompleted_rejection_in_or_rejection_out(doctype, txt, searchfield, start, page_len, filters):
    new_filters = {
        "stock_entry_type": filters.get("stock_entry_type"),
        "selco_branch": filters.get("selco_branch"),
        "selco_supplier_or_customer_id": filters.get("selco_supplier_or_customer_id"),
        "txt": "%%%s%%" % txt,
        "start": start,
        "page_len": page_len
    }

    return frappe.db.sql(""" SELECT distinct se.name from `tabStock Entry` se, `tabStock Entry Detail` sei
        where se.stock_entry_type = %(stock_entry_type)s and se.name = sei.parent and ifnull(sei.reference_rej_in_or_rej_quantity,0) < sei.qty
        and se.docstatus = 1 and se.selco_branch = %(selco_branch)s and 
        se.selco_supplier_or_customer_id = %(selco_supplier_or_customer_id)s
        and se.name like %(txt)s limit %(start)s, %(page_len)s
    """, new_filters)


def validate_back_dated_entries(doc, method):
        if frappe.session.user == "Administrator":
                return
        no_of_days = cint(frappe.db.get_single_value("Accounts Settings", "no_of_days"))
        allow_to_edit_role = frappe.db.get_single_value("Accounts Settings", "allow_to_edit_role") or "SELCO Edit Posting Date"
        if doc.doctype in ["Stock Entry", "Payment Entry", "Journal Entry", "Sales Invoice", "Delivery Note"] and no_of_days:
                if allow_to_edit_role in frappe.get_roles() and getdate(doc.posting_date) < getdate(add_days(today(), -1 * no_of_days)):
                        frappe.throw(_("User don't have permission to submit the back dated {0}, please contact to administrator").format(doc.doctype))
        if (doc.doctype in ["Stock Entry", "Payment Entry", "Journal Entry", "Sales Invoice", "Delivery Note"]
                and allow_to_edit_role not in frappe.get_roles() and getdate(doc.posting_date) < getdate(add_days(today(), -1))):
                frappe.throw(_("User don't have permission to submit the back dated {0}, please contact to administrator").format(doc.doctype))
