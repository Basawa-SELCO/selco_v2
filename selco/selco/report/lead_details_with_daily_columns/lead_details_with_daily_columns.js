// Copyright (c) 2016, SELCO and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Lead Details with Daily Columns"] = {
	"filters": [
	{
	"fieldname": "fiscal_year",
	"label": __("Fiscal Year"),
	"fieldtype": "Link",
	"options": "Fiscal Year",
	default: "2018-2019"
	},
	{
	"fieldname":"month_number",
	"label": __("Month"),
	"fieldtype": "Select",
	"options": "Jan\nFeb\nMar\nApr\nMay\nJun\nJul\nAug\nSep\nOct\nNov\nDec",
	"default": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov",
	"Dec"][frappe.datetime.str_to_obj(frappe.datetime.get_today()).getMonth()],
	}
	],
}

