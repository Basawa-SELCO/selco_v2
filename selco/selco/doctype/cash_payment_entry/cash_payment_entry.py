# -*- coding: utf-8 -*-
# Copyright (c) 2017, SELCO and contributors
# For license information, please see license.txt

# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class CashPaymentEntry(Document):
	def before_insert(self):
		frappe.msgprint('jkl')
		self.naming_series = frappe.db.get_value("Branch",self.selco_branch,"cash_payment_naming_series")

	def on_submit(self):
		je = frappe.new_doc('Journal Entry')
		frappe.msgprint('jkl')
		je.selco_branch = self.selco_branch
		je.name = "J" + self.name
		je.naming_series = "J" + frappe.db.get_value("Branch",self.selco_branch,"cash_payment_naming_series")
		je.voucher_type = self.voucher_type
		je.posting_date = self.posting_date
		je.company = self.company
		for d in self.get('accounts'):
			je.append("accounts",{
			"account":d.account,
			"cost_center":d.cost_center,
			"account_currency":d.account_currency,
			"debit_in_account_currency":d.debit_in_account_currency,
			"credit_in_account_currency":d.credit_in_account_currency
			})
		je.save()
		je.submit()
