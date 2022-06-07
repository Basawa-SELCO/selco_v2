import frappe
import json
from frappe import _

# @frappe.whitelist()
# def get_installation_note():
# 	data = frappe.get_all("Installation Note")
# 	data_list = []

# 	parent_fields = ['name','selco_branch','naming_series','status','selco_payment_entry_number','customer_group','customer','customer_name','territory','customer_address','address_display','selco_customer_contact_number','selco_landline_mobile_2','selco_sales_person','selco_warranty_terms1','inst_date','selco_installation_start_date','selco_installation_end_date','inst_time','selco_delivery_note_date','selco_electrification_status','selco_concealed','selco_piping','selco_cnc','selco_length_of_hot_water_line','selco_length_of_cold_water_line','selco_taps','selco_non_return_valves','selco_gate_valve','selco_oht_height','selco_customer_remarks','selco_customer_feedback','selco_cse_remarks','selco_cse_feedback','selco_cse_name','selco_cse_name_1','selco_signature_of_customer','selco_cse_date','selco_customer_name','selco_custmer_date','selco_terms_and_conditions','selco_cse_location']
	
# 	child_fields = ['name','idx','parent','parenttype','item_code','item_name','selco_make','description','selco_number_of_years','selco_item_group','qty','uom','selco_serial_number']
 
# 	for row in data:
# 		parent_dict = frappe.db.get_value("Installation Note",row.name,parent_fields, as_dict=True)

# 		parent_dict['packed_items'] = frappe.db.get_values("Packed Item",{'parenttype':'Installation Note','parent':row.name},child_fields, as_dict=True)
		
# 		data_list.append(parent_dict)

# 	return data_list

@frappe.whitelist()
def get_installation_note():
	if frappe.request.data:
		request_data = json.loads(frappe.request.data)
		if request_data.get("filters").get('sync_date'):
			date = request_data.get("filters").get('sync_date')
			data = frappe.get_list("Installation Note",filters={'creation':date,'modified':date,'docstatus':['!=',2]})
		else:
			data = frappe.get_list("Installation Note",{'docstatus':['!=',2]})
	else:
		data = frappe.get_list("Installation Note",{'docstatus':['!=',2]})

	data_list = []
	parent_fields = ['name','selco_branch','naming_series','status','selco_payment_entry_number','customer_group','customer','customer_name','territory','customer_address','address_display','selco_customer_contact_number','selco_landline_mobile_2','selco_sales_person','selco_warranty_terms1','inst_date','selco_installation_start_date','selco_installation_end_date','inst_time','selco_delivery_note_date','selco_electrification_status','selco_concealed','selco_piping','selco_cnc','selco_length_of_hot_water_line','selco_length_of_cold_water_line','selco_taps','selco_non_return_valves','selco_gate_valve','selco_oht_height','selco_customer_remarks','selco_customer_feedback','selco_cse_remarks','selco_cse_feedback','selco_cse_name','selco_cse_name_1','selco_signature_of_customer','selco_cse_date','selco_customer_name','selco_custmer_date','selco_terms_and_conditions','selco_cse_location','selco_electrification_status']
	child_fields = ['name','idx','parent','parenttype','item_code','item_name','selco_make','description','selco_number_of_years','selco_item_group','qty','uom','selco_serial_number']
 
	for row in data:
		parent_dict = frappe.db.get_value("Installation Note",row.name,parent_fields, as_dict=True)
		parent_dict['selco_taluk'] = frappe.db.get_value("Address",parent_dict['customer_address'],'selco_taluk')
		parent_dict['selco_local_area'] = frappe.db.get_value("Address",parent_dict['customer_address'],'selco_local_area')
		parent_dict['packed_items'] = frappe.db.get_values("Packed Item",{'parenttype':'Installation Note','parent':row.name},child_fields, as_dict=True)
		data_list.append(parent_dict)

	return data_list

@frappe.whitelist(methods=["PUT"])
def update_installation_note():
	if frappe.request.data:
		request_data = json.loads(frappe.request.data)
		if not request_data.get("name"):
			frappe.throw("Define name to update the record")
		if not frappe.db.exists("Installation Note",request_data.get("name")):
			frappe.throw("Installation Note {} not exists.".format(request_data.get("name")))
		doc = frappe.get_doc("Installation Note",request_data.get("name"))
		if not doc.has_permission("read") or not doc.has_permission("write"):
			frappe.throw(_("Not permitted"), frappe.PermissionError)
		if doc.docstatus == 1:
			frappe.throw("Installation Note {} is Submitted.Can not edit submitted document".format(request_data.get("name")))
		if doc.docstatus == 2:
			frappe.throw("Installation Note {} is Cancelled.Can not edit cancelled document".format(request_data.get("name")))
		
		parent_field_list = ['selco_customer_contact_number','selco_landline_mobile_2','selco_warranty_terms1','selco_installation_start_date','selco_installation_end_date','selco_electrification_status','selco_concealed','selco_piping','selco_cnc','selco_length_of_hot_water_line','selco_length_of_cold_water_line','selco_taps','selco_non_return_valves','selco_gate_valve','selco_oht_height','selco_customer_remarks','selco_customer_feedback','selco_cse_remarks','selco_cse_feedback','selco_cse_name','selco_customer_name','selco_cse_location','selco_electrification_status','submitted']
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
	if request_data.get("packed_items"):
		child_field_list = ['selco_make','description','selco_serial_number']
		for row in request_data.get("packed_items"):
			if not row.get('name'):
				frappe.throw('Define name in packed_items to update child record.')
			if not frappe.db.exists("Packed Item",{'name':row.get('name'),'parent':request_data.get('name')}):
				frappe.throw("Installation Note packed items {} not exists.".format(row.get("name")))
			for child_field in child_field_list:
				if row.get(child_field):
					for item in doc.packed_items:
						if item.name == row.get('name'):
							item.db_set(child_field,row.get(child_field))
