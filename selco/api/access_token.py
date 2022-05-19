import frappe
from frappe.utils.password import check_password

@frappe.whitelist(allow_guest=True)
def get_access_api_token(usr, pwd):
	access_api_token = {}
	try:
		check_password(usr,pwd)
	except Exception as e:
		return e
	doc = frappe.get_doc("User", {'name':usr})
	api_key = doc.api_key
	api_secret = doc.get_password('api_secret')
	if api_key and api_secret:
		api_token = "token "+api_key+":"+api_secret
		access_api_token = {"access_token": api_token,'email':usr}
			
	return access_api_token 