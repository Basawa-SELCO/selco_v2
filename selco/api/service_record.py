import frappe
import json
from frappe import _


# @frappe.whitelist()
# def get_service_record():
# 	data = frappe.get_all("Service Record")
# 	data_list = []

# 	parent_fields = ['name','selco_complaint_date','docstatus','selco_customer_feedback','selco_service_charges_collected','selco_detail_address','selco_customer_address','selco_customer_remarks','selco_customer_signature','selco_customer_date','selco_landline_mobile_2','selco_cse_location','selco_branch','selco_posting_date','selco_cse_feedback','selco_job_status','selco_cse_name','selco_customer_contact_number','selco_signature_of_the_cse','selco_cse_signature','selco_signature_of_the_customer','selco_customer_id','selco_cse_remarks','selco_complaint_number','selco_cse_date','selco_customer_full_name']
	
# 	child_fields = ['name','idx','parent','parenttype','selco_within_warranty','selco_serial_number','selco_collected_amount','selco_make','selco_item_name','selco_specs','selco_item_code','selco_remarks']
 
# 	for row in data:
# 		parent_dict = frappe.db.get_value("Service Record",row.name,parent_fields, as_dict=True)

# 		parent_dict['selco_fault_rectified_and_replacement_detail'] = frappe.db.get_values("Service Record Item Details",{'parenttype':'Service Record','parent':row.name},child_fields, as_dict=True)
		
		
# 		data_list.append(parent_dict)

# 	return data_list


@frappe.whitelist()
def get_service_record():
	if frappe.request.data:
		request_data = json.loads(frappe.request.data)
		if request_data.get("filters").get('sync_date'):
			date = request_data.get("filters").get('sync_date')
			data = frappe.get_list("Service Record",filters={'creation':date,'modified':date,'docstatus':['!=',2]})
		else:
			data = frappe.get_list("Service Record",{'docstatus':['!=',2]})
	else:
		data = frappe.get_list("Service Record",{'docstatus':['!=',2]})

	data_list = []
	parent_fields = ['name','selco_complaint_date','docstatus','selco_customer_feedback','selco_service_charges_collected','selco_detail_address','selco_customer_address','selco_customer_remarks','selco_customer_signature','selco_customer_date','selco_landline_mobile_2','selco_cse_location','selco_branch','selco_posting_date','selco_cse_feedback','selco_job_status','selco_cse_name','selco_customer_contact_number','selco_signature_of_the_cse','selco_cse_signature','selco_signature_of_the_customer','selco_customer_id','selco_cse_remarks','selco_complaint_number','selco_cse_date','selco_customer_full_name','selco_taluk']
	child_fields = ['name','idx','parent','parenttype','selco_within_warranty','selco_serial_number','selco_collected_amount','selco_make','selco_item','selco_item_name','selco_specs','selco_item_code','selco_remarks']
 
	for row in data:
		parent_dict = frappe.db.get_value("Service Record",row.name,parent_fields, as_dict=True)
		parent_dict['selco_taluk'] = frappe.db.get_value("Address",parent_dict['selco_customer_address'],'selco_taluk')
		parent_dict['selco_local_area'] = frappe.db.get_value("Address",parent_dict['selco_customer_address'],'selco_local_area')
		parent_dict['selco_fault_rectified_and_replacement_detail'] = frappe.db.get_values("Service Record Item Details",{'parenttype':'Service Record','parent':row.name},child_fields, as_dict=True)
		data_list.append(parent_dict)

	return data_list

@frappe.whitelist(methods=["PUT"])
def update_service_record():
	if frappe.request.data:
		request_data = json.loads(frappe.request.data)
		if not request_data.get("name"):
			frappe.throw("Define name to update the record")
		if not frappe.db.exists("Service Record",request_data.get("name")):
			frappe.throw("Service Record {} not exists.".format(request_data.get("name")))
		doc = frappe.get_doc("Service Record",request_data.get("name"))
		if not doc.has_permission("read") or not doc.has_permission("write"):
			frappe.throw(_("Not permitted"), frappe.PermissionError)
		if doc.docstatus == 1:
			frappe.throw("Service Record {} is Submitted.Can not edit submitted document".format(request_data.get("name")))
		if doc.docstatus == 2:
			frappe.throw("Service Record {} is Cancelled.Can not edit cancelled document".format(request_data.get("name")))
		
		parent_field_list = ['selco_customer_feedback','selco_service_charge_collected','selco_customer_remarks','selco_customer_signature','selco_cse_location','selco_cse_feedback','selco_job_status','selco_cse_name','selco_cse_signature','selco_customer_id','selco_cse_remarks','selco_complaint_number','selco_cse_date','submitted']
		for field in parent_field_list:
				if request_data.get(field):
					if field == "submitted":
						doc.submitted = request_data.get(field)
					else:
						doc.db_set(field, request_data.get(field))
		update_child_records(request_data, doc)
		doc.save()
		if doc.get('submitted'):
			doc.submit()
		frappe.db.commit()
		doc.reload()
		return doc

def update_child_records(request_data, doc):
	if request_data.get("selco_fault_rectified_and_replacement_detail"):
		child_field_list = ['selco_item','selco_within_warranty','selco_serial_number','selco_collected_amount','selco_make','selco_remarks']
		for row in request_data.get("selco_fault_rectified_and_replacement_detail"):
			if not row.get('name'):
				frappe.throw('Define name in selco_fault_rectified_and_replacement_detail to update child record.')
			if not frappe.db.exists("Service Record Item Details",{'name':row.get('name'),'parent':request_data.get('name')}):
				frappe.throw("Service Record Item Details {} not exists.".format(row.get("name")))
			for child_field in child_field_list:
				if row.get(child_field):
					for item in doc.selco_fault_rectified_and_replacement_detail:
						if item.name == row.get('name'):
							item.db_set(child_field,row.get(child_field))
