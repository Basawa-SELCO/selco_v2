import frappe
import json
from frappe import _

# from frappe.handler import upload_file
# @frappe.whitelist()
# def get_maintenance_visit():
# 	data = frappe.get_list("Maintenance Visit")
# 	data_list = []

# 	parent_fields = ['name','selco_branch','customer','customer_name','address_display','selco_customer_contact_number','selco_customer_landline_number','selco_payment_entry_number','mntc_date','completion_status','maintenance_type','status','selco_total_component_charges_collected','selco_service_charges_collected','selco_total_amount','selco_cse_remarks','selco_cse_feedback','selco_signature_of_the_customer','selco_cse_signature','selco_signature_of_the_cse','selco_cse_location','selco_customer_remarks','selco_customer_feedback','customer_address','selco_customers_signature','naming_series','maintenance_schedule','maintenance_schedule_detail','mntc_time','company','customer_group']
	
# 	child_fields = ['name','idx','parent','parenttype','item_code','selco_item_group','item_name','selco_make','selco_quantity','selco_serial_number','selco_specs','selco_specs','service_person','description','work_done','selco_collected_amount']
 
# 	for row in data:
# 		# parent_dict = frappe.db.sql("""
# 		# 	select {parent_fields}
# 		# 	from `tabMaintenance Visit` 
# 		# 	where name = '{name}'
# 		# """.format(**{"parent_fields": ", ".join(parent_fields),"name": row.name}),as_dict=True)[0]

# 		# parent_dict['purposes'] =frappe.db.sql("""
# 		# 	select {child_fields} 
# 		# 	from `tabMaintenance Visit Purpose` 
# 		# 	where parent = '{parent}'
# 		# """.format(**{"child_fields": ", ".join(child_fields),'parent':row.name}),as_dict=True)
		
# 		parent_dict = frappe.db.get_value("Maintenance Visit",row.name,parent_fields, as_dict=True)

# 		parent_dict['purposes'] = frappe.db.get_values("Maintenance Visit Purpose",{'parenttype':'Maintenance Visit','parent':row.name},child_fields, as_dict=True)

# 		data_list.append(parent_dict)

# 	return data_list

@frappe.whitelist()
def get_maintenance_visit():
	if frappe.request.data:
		request_data = json.loads(frappe.request.data)
		if request_data.get("filters").get('sync_date'):
			date = request_data.get("filters").get('sync_date')
			data = frappe.get_list("Maintenance Visit",filters={'creation':date,'modified':date,'docstatus':['!=',2]})
		else:
			data = frappe.get_list("Maintenance Visit",{'docstatus':['!=',2]})
	else:
		data = frappe.get_list("Maintenance Visit",{'docstatus':['!=',2]})

	data_list = []
	parent_fields = ['name','selco_branch','customer','customer_name','address_display','selco_customer_contact_number','selco_customer_landline_number','selco_payment_entry_number','mntc_date','completion_status','maintenance_type','status','selco_total_component_charges_collected','selco_service_charges_collected','selco_total_amount','selco_cse_remarks','selco_cse_feedback','selco_signature_of_the_customer','selco_cse_signature','selco_signature_of_the_cse','selco_cse_location','selco_customer_remarks','selco_customer_feedback','customer_address','selco_customers_signature','naming_series','maintenance_schedule','maintenance_schedule_detail','mntc_time','company','customer_group','selco_taluk','selco_sales_person','selco_service_person','selco_customer_date','selco_cse_date']	
	child_fields = ['name','idx','parent','parenttype','item_code','selco_item_group','item_name','selco_make','selco_quantity','selco_serial_number','selco_specs','service_person','description','work_done','selco_collected_amount']
 
	for row in data:
		parent_dict = frappe.db.get_value("Maintenance Visit",row.name,parent_fields, as_dict=True)
		parent_dict['selco_taluk'] = frappe.db.get_value("Address",parent_dict['customer_address'],'selco_taluk')
		parent_dict['selco_local_area'] = frappe.db.get_value("Address",parent_dict['customer_address'],'selco_local_area')
		parent_dict['purposes'] = frappe.db.get_values("Maintenance Visit Purpose",{'parenttype':'Maintenance Visit','parent':row.name},child_fields, as_dict=True)
		data_list.append(parent_dict)

	return data_list

@frappe.whitelist(methods=["PUT"])
def update_maintenance_visit():
	if frappe.request.data:
		request_data = json.loads(frappe.request.data)
		if not request_data.get("name"):
			frappe.throw("Define name to update the record")
		if not frappe.db.exists("Maintenance Visit",request_data.get("name")):
			frappe.throw("Maintenance Visit {} not exists.".format(request_data.get("name")))
		doc = frappe.get_doc("Maintenance Visit",request_data.get("name"))
		if not doc.has_permission("read") or not doc.has_permission("write"):
			frappe.throw(_("Not permitted"), frappe.PermissionError)
		if doc.docstatus == 1:
			frappe.throw("Maintenance Visit {} is Submitted.Can not edit submitted document".format(request_data.get("name")))
		if doc.docstatus == 2:
			frappe.throw("Maintenance Visit {} is Cancelled.Can not edit cancelled document".format(request_data.get("name")))
		# if doc.completion_status == "Fully Completed":
		# 	frappe.throw("Maintenance Visit {} is Fully Completed.".format(request_data.get("name")))
		parent_field_list = ['completion_status','selco_customer_contact_number','selco_customer_landline_number','selco_service_charges_collected','selco_cse_remarks','selco_cse_feedback','selco_cse_signature','selco_cse_location','selco_customer_remarks','selco_customer_feedback','selco_customers_signature','submitted']
		for field in parent_field_list:
			if request_data.get(field):
				if field == "submitted":
					doc.submitted = request_data.get(field)
				else:
					doc.db_set(field, request_data.get(field))
		update_child_records(request_data,doc)
		doc.save()
		if doc.get('submitted'):
			doc.submit()
		frappe.db.commit()
		doc.reload()
		return doc

def update_child_records(request_data,doc):
	if request_data.get("purposes"):
		child_field_list = ['selco_make','selco_specs','selco_serial_number','description','work_done','selco_collected_amount']
		for row in request_data.get("purposes"):
			if not row.get('name'):
				frappe.throw('Define name in purposes to update child record.')
			if not frappe.db.exists("Maintenance Visit Purpose",{'name':row.get('name'),'parent':request_data.get('name')}):
				frappe.throw("Maintenance Visit Purpose {} not exists.".format(row.get("name")))
			for child_field in child_field_list:
				if row.get(child_field):
					for item in doc.purposes:
						if item.name == row.get('name'):
							item.db_set(child_field,row.get(child_field))