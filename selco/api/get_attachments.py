import frappe
from frappe.desk.form.load import get_attachments

@frappe.whitelist()
def get_doc_attachments(doctype, docname):
	if not doctype:
		frappe.throw("Define Doctype to get attachments.")
	if not docname:
		frappe.throw("Define Docname to get attachments.")
	if not frappe.db.exists(doctype,docname):
		frappe.throw(f"{doctype} {docname} not exists.")
	attachments = get_attachments(doctype,docname)
	return attachments