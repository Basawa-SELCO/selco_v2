# Copyright (c) 2013, SELCO and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from erpnext.hr.doctype.payroll_entry.payroll_entry import get_month_details
from frappe import msgprint
import datetime
from datetime import timedelta
from frappe.utils import cint, flt, nowdate,getdate

def execute(filters=None):
	columns, data = [], []
	columns = get_columns()
	issue_list1 = get_details(filters)
	for d in issue_list1:
		data.append(d)
	return columns, data

def get_columns():
	return [
		_("Complaint ID ") + ":Link/Issue:180",_("Branch") + ":Data:180", _("Complaint Recieved date") + "Date:180",_("Customer Name") + ":Data:180",_("Customer Address") + ":Data:180",_("Contact Number") + ":Data:180",_("Nature of Complaint") + ":Data:180",_("Created By") + ":Data:180",_("Attended By") + ":Data:180",_("Status") + ":Data:180",_("Service Record Number") + ":Data:180",_("Service Record Date") + ":Data:180",_("Remarks") + ":Data:180"
		]

def get_details(filters):
	conditions = ""
	values = []
	msd = "0000/00/00"
	med = "0000/00/00"
	fiscal_year = filters.get("fiscal_year")
	if filters.get("fiscal_year"):
		month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov",
			"Dec"].index(filters["month_number"]) + 1
		ysd = frappe.db.get_value("Fiscal Year", fiscal_year, "year_start_date")
		from dateutil.relativedelta import relativedelta
		import calendar, datetime
		diff_mnt = cint(month)-cint(ysd.month)
		if diff_mnt<0:
			diff_mnt = 12-int(ysd.month)+cint(month)
		msd = ysd + relativedelta(months=diff_mnt) # month start date
		month_days = cint(calendar.monthrange(cint(msd.year) ,cint(month))[1]) # days in month
		med = datetime.date(msd.year, cint(month), month_days) # month end date
	var1 = filters.get("ss")
	return frappe.db.sql("""select name,selco_branch, selco_complaint_received_date, selco_customer_full_name, selco_detail_address, selco_customer_contact_number, selco_description_of_complaint, owner, selco_complaint_handled_by_cse, workflow_state, selco_service_record_number_1, selco_service_record_date, selco_branch_remarks from `tabIssue` where selco_service_branch_email_id = %s AND selco_complaint_received_date BETWEEN %s AND %s AND docstatus!=2 """, (var1,msd,med))
