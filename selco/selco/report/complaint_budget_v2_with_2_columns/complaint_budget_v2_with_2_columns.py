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
	data = []

	issue_list1 = get_sr_details(filters)
	var1=0
	for d in issue_list1:
		if d.special_budget_approved_by_csd>0:
			var1=0
			var2=d.special_budget_approved_by_csd
		elif d.within_warranty:
			var1=70
			var2=0
		elif d.budget_thirty_five:
			var1=0
			var2=0.35*d.service_amount
		else:
			var1=0
			var2=0
		row = [d.name,d.selco_customer_full_name,d.selco_service_person,d.selco_service_record_number_1,d.service_amount,var1,var2,d.selco_remarks]
		data.append(row)
		var1=0
		var2=0

	return columns, data


def get_columns():
	return [
		_("Complaint ID ") + ":Link/Issue:180", _("Customer Name") + ":Data:180",_("Service Person Name") + ":Link/Service Person:180",_("Service Record Number") + ":Data:180",_("Service Charges Collected") + ":Currency:180",_("Budget Approved within warranty") + ":Currency:180",_("Budget Approved 35%") + ":Currency:180",_("CSD Remarks") + ":Data:180"
		]


def get_sr_details(filters):

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
	selco_branch = filters.get("branch")
	# return frappe.db.sql("""select name, date, customer_full_name, ics_date, complaint_handled_by,special_budget,service_charges_collected,service_record_number,remarks from `tabIssue` where (workflow_state="Complaint Closed By Branch") AND service_branch_email_id = %s AND complaint_closed_date BETWEEN %s AND %s""", (selco_branch,msd,med),as_dict=1)
	# return frappe.db.sql("""SELECT A.name,A.selco_customer_full_name,A.selco_ics_date,A.selco_remarks,B.service_record_number,B.service_person,B.service_record_date,B.service_amount,B.within_warranty,B.approve_budget FROM `tabIssue` AS A INNER JOIN `tabService Record Details Issue` AS B ON A.name=B.parent WHERE A.workflow_state = "Complaint Closed By Branch" AND A.name="COMP/TUM/16-17/00014" AND A.selco_service_branch_email_id = %s AND B.service_record_date BETWEEN %s AND %s""", (selco_branch,msd,med),as_dict=1)
	return frappe.db.sql("""SELECT A.name, A.selco_complaint_received_date, A.selco_customer_full_name, A.selco_ics_date, A.selco_remarks, B.service_record_number, B.service_person, B.service_record_date, B.service_amount, B.within_warranty, B.special_budget_approved_by_csd, B.approve_budget, B.csd_remarks FROM `tabIssue` AS A INNER JOIN `tabService Record Details Issue` AS B ON A.name=B.parent WHERE selco_service_branch_email_id = %s AND B.service_record_date BETWEEN %s AND %s""", (selco_branch,msd,med),as_dict=1)