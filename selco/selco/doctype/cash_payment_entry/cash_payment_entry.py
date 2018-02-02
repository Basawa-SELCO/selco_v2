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
        self.naming_series = frappe.db.get_value("Branch",self.selco_branch,"selco_cash_payment_naming_series")

    def on_submit(self):
        je = frappe.new_doc('Journal Entry')
        je.selco_branch = self.selco_branch
        je.voucher_type = self.voucher_type
        je.selco_use_different_cost_center = self.use_different_cost_center
        je.posting_date = self.posting_date
        je.cheque_no = self.cheque_no
        je.cheque_date = self.cheque_date
        je.user_remark = self.user_remark
        je.name = "J" + self.name
        frappe.msgprint("je.name is" + str(je.name))
        je.company = self.company
        for d in self.get('accounts'):
            je.append("accounts",{
                "account":d.account,
                "party_type":d.party_type,
                "party":d.party,
                "reference_type":d.reference_type,
                "reference_name":d.reference_name,
                "is_advance":d.is_advance,
                 "cost_center":d.cost_center,
                 "account_currency":d.account_currency,
                "debit_in_account_currency":d.debit_in_account_currency,
                "credit_in_account_currency":d.credit_in_account_currency
            })
        je.save()
        je.submit()
