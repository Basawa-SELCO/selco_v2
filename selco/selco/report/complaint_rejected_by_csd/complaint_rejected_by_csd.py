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

	issue_list4 = get_details_complaint_rejected_csd(filters)

	for d in issue_list4:
		row = []
		no_of_sr = 0
		ics_last_year = d.selco_complaint_received_date - timedelta(days=365)
		sr_details = d.selco_service_record_number_1
		if sr_details is not None:
			no_of_sr = len(sr_details.split("/"))
		if d.special_budget:
			row = [d.name, d.selco_customer_full_name, d.selco_complaint_handled_by_cse,d.selco_service_charges_collected,d.selco_special_budget,d.selco_special_budget,d.selco_remarks]
		elif (d.ics_date and (getdate(d.ics_date) > ics_last_year)):
			row = [d.name, d.selco_customer_full_name, d.selco_complaint_handled_by_cse,d.selco_service_charges_collected,70,0,d.selco_remarks]
		else:
			#d.service_charges_collected = d.service_charges_collected * 0.35
			row = [d.name, d.selco_customer_full_name, d.selco_complaint_handled_by_cse,d.selco_service_charges_collected,d.selco_service_charges_collected * 0.35,0,d.selco_remarks]
		data.append(row)

	return columns, data
def get_columns():
	return [
		_("Complaint ID ") + ":Link/Issue:180", _("Customer Name") + ":Data:180",_("Service Person Name") + ":Link/Service Person:180",_("Service Charges Collected") + ":Currency:180",_("Budget As Per Branch") + ":Currency:180",_("Budget As Per CSD") + ":Currency:180", _("CSD Remarks") + ":Data:180"
		]

def get_details_complaint_rejected_csd(filters):
	conditions = ""
	values = []
	msd = "0000/00/00"
	med = "0000/00/00"
	fiscal_year = filters.get("fiscal_year")
	if filters.get("fiscal_year"):
		month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov",
			"Dec"].index(filters["month_number"]) + 1
		ysd = frappe.db.get_value("Fiscal Year", fiscal_year, "year_start_date")
		#frappe.msgprint(ysd)
		from dateutil.relativedelta import relativedelta
		import calendar, datetime
		diff_mnt = cint(month)-cint(ysd.month)
		if diff_mnt<0:
			diff_mnt = 12-int(ysd.month)+cint(month)
		msd = ysd + relativedelta(months=diff_mnt) # month start date
		month_days = cint(calendar.monthrange(cint(msd.year) ,cint(month))[1]) # days in month
		med = datetime.date(msd.year, cint(month), month_days) # month end date
	selco_branch = filters.get("ss")
	selco_service_person = filters.get("selco_service_person")
	if selco_service_person:
		return frappe.db.sql("""select name, selco_complaint_received_date, selco_customer_full_name, selco_ics_date, selco_complaint_handled_by_cse,selco_special_budget,selco_service_charges_collected,selco_service_record_number_1,selco_service_record_number_2,selco_remarks from `tabIssue` where (workflow_state="Complaint Rejected By CSD") AND selco_service_branch_email_id = %s AND selco_complaint_closed_date BETWEEN %s AND %s AND selco_complaint_handled_by_cse LIKE %s""", (selco_branch,msd,med,selco_service_person),as_dict=1)
	else:
		return frappe.db.sql("""select name, selco_complaint_received_date, selco_customer_full_name, selco_ics_date, selco_complaint_handled_by_cse,selco_special_budget,selco_service_charges_collected,selco_service_record_number_1,selco_service_record_number_2,selco_remarks from `tabIssue` where (workflow_state="Complaint Rejected By CSD") AND selco_service_branch_email_id = %s AND selco_complaint_closed_date BETWEEN %s AND %s""", (selco_branch,msd,med),as_dict=1)
