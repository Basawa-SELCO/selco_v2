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

months = {
	"Jan"  :"January",
	"Feb"  :"February",
	"Mar"  :"March",
	"Apr"  :"April",
	"May"  :"May",
	"Jun"  :"June",
	"Jul"  :"July",
	"Aug"  :"August",
	"Sep"  :"September",
	"Oct"  :"October",
	"Nov"  :"November",
	"Dec"  :"December",
}

def execute(filters):
	columns, data, initial = [], [],[]
	columns= get_columns()
	#unorganized data
	initial = get_data(filters)	

	ins_sb=[]						#insentive service
	ins_ist=[]						#insentive installation
	no_sb=[]						#no insentive service
	no_ist=[]						#no insentive installation
	total_ins=[]					#total insentive eligibe CSE
	total_no=[]						#total insentive uneligible CSE

	for d in initial:
		if d[5]=="Service" :
			if int(d[6])>99 :
				ins_sb.append(d)
			else :
				no_sb.append(d)
		else:
			if int(d[6]>53) :
				ins_ist.append(d)
			else :
				no_ist.append(d)

	if(len(initial)>0):
		total_ins=[""]*len(initial[0])
		total_no=[""]*len(initial[0])
		info_sb=[""]*len(initial[0])											#string info service with insentive
		info_no_sb=[""]*len(initial[0])											#string info service without insentive
		info_ins=[""]*len(initial[0])											#string info Installation with insentive
		info_no_ins=[""]*len(initial[0])										#string info Installation without insentive
	else:
		return columns, data


	tot_ins = len(ins_sb)+len(ins_ist)											#Total eligible CSE
	tot_no = len(no_sb)+len(no_ist)												#Total uneligible CSE
	total_ins[2]='<b>&nbsp;&emsp;&emsp;<u>TOTAL</u>-</b>'
	total_ins[3]='<b><u>ELIGIBLE CSE</u> : </b>'+'<b>'+str(tot_ins)+'</b>'
	total_no[2]='<b>&emsp;&emsp;&nbsp;<u>TOTAL</u>-</b>'
	total_no[3]='<b><u>UNELIGIBLE CSE</u> : </b>'+'<b>'+str(tot_no)+'</b>'
	
	data.append(total_ins)
	data.append(total_no)

	if(len(ins_sb)>0):

		info_sb[0]='<center><u><b>Eligible CSE (Service) : </u></center></b>'#+ str((len(ins_sb)))+'</b>'
		info_sb[1]='<b>'+str((len(ins_sb)))+'</b>'
		data.append(info_sb)
		data=data+ins_sb

	if(len(no_sb)>0):

		info_no_sb[0]='<center><u><b>Ineligible CSE (Service) : </u></center></b>' #+ str(len(no_sb))+'</b>'
		info_no_sb[1]='<b>'+ str(len(no_sb))+'</b>'
		data.append(info_no_sb)
		data=data+no_sb

	if(len(ins_ist)>0):

		info_ins[0]='<center><u><b>Eligible CSE(Installation):</u></center></b>'#+str(len(ins_ist))+'</b>'
		info_ins[1]='<b>'+str(len(ins_ist))+'</b>'
		data.append(info_ins)
		data=data+ins_ist

	if(len(no_ist)>0):

		info_no_ins[0]='<center><u><b>Inligible CSE(Installation):</u></center></b>'#+ str(len(no_ist))+'</b>'
		info_no_ins[1]='<b>'+ str(len(no_ist))+'</b>'
		data.append(info_no_ins)
		data=data+no_ist

	total=get_sum(initial)			
	data.append(total)



	return columns, data

def get_columns():
	return[
	("Branch")+":Link/Branch:165",
	("Sr. MGR Name")+":Link/Service Person:135",
	("P/T")+":Data:80",
	("Name of CSE")+":Link/Service Person:140",
	("CSE Contact No")+":Data:100",
	("Service/Installation")+":Data:85",
	("Row Total")+":Data:75",
	("Day 1")+":Data:50",("Day 2")+":Data:50",("Day 3")+":Data:50",("Day 4")+":Data:50",
	("Day 5")+":Data:50",("Day 6")+":Data:50",("Day 7")+":Data:50",("Day 8")+":Data:50",
	("Day 9")+":Data:50",("Day 10")+":Data:50",("Day 11")+":Data:50",("Day 12")+":Data:50",
	("Day 13")+":Data:50",("Day 14")+":Data:50",("Day 15")+":Data:50",("Day 16")+":Data:50",
	("Day 17")+":Data:50",("Day 18")+":Data:50",("Day 19")+":Data:50",("Day 20")+":Data:50",
	("Day 21")+":Data:50",("Day 22")+":Data:50",("Day 23")+":Data:50",("Day 24")+":Data:50",
	("Day 25")+":Data:50",("Day 26")+":Data:50",("Day 27")+":Data:50",("Day 28")+":Data:50",
	("Day 29")+":Data:50",("Day 30")+":Data:50",("Day 31")+":Data:50"

	]

def get_data(filters):
	mnth=filters.get("month")
	mnth = months.get(mnth)
	return frappe.db.sql("""
	SELECT A.selco_branch, C.selco_reports_to, C.selco_status, B.service_person, C.selco_contact_number, C.selco_service_or_installation,
	B.day_1+B.day_2+B.day_3+B.day_4+B.day_5+B.day_6+B.day_7+B.day_8+B.day_9+B.day_10+B.day_11+B.day_12+B.day_13+B.day_14+B.day_15+B.day_16+
	B.day_17+B.day_18+B.day_19+B.day_20+B.day_21+B.day_22+B.day_23+B.day_24+B.day_25+B.day_26+B.day_27+B.day_28+B.day_29+B.day_30+B.day_31,
	B.day_1, B.day_2, B.day_3, B.day_4, B.day_5, B.day_6, B.day_7, B.day_8, B.day_9, B.day_10, B.day_11, B.day_12, B.day_13, B.day_14, B.day_15, B.day_16,
	B.day_17, B.day_18, B.day_19, B.day_20, B.day_21, B.day_22, B.day_23, B.day_24, B.day_25, B.day_26, B.day_27, B.day_28, B.day_29, B.day_30, B.day_31
	FROM `tabService Call` AS A INNER JOIN `tabService Call Details` AS B INNER JOIN `tabService Person` AS C ON A.name=B.parent
	AND B.service_person=C.name
	WHERE A.selco_month= %s
	ORDER BY B.day_1+B.day_2+B.day_3+B.day_4+B.day_5+B.day_6+B.day_7+B.day_8+B.day_9+B.day_10+
	B.day_11+B.day_12+B.day_13+B.day_14+B.day_15+B.day_16+B.day_17+B.day_18+B.day_19+B.day_20+B.day_21+B.day_22+B.day_23+B.day_24+B.day_25+
	B.day_26+B.day_27+B.day_28+B.day_29+B.day_30+B.day_31 DESC""",(mnth),as_list=1)
	#sum of calls for each day

def get_sum(data):
	total=[0]*len(data[0])

	for i in range(0,len(data)) :
		for j in range(7,len(data[i])) :
			total[j]=total[j]+data[i][j]

	total[6]="<b>Col Total</b>"
	for i in range(0,6):
		total[i]=""
	return total