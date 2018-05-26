# Copyright (c) 2013, SELCO and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, getdate

def execute(filters=None):
    if not filters: filters = {}

    validate_filters(filters)

    columns = get_columns()
    item_map = get_item_details(filters)
    iwb_map = get_item_warehouse_map(filters)

    data = []
    for (company, item, warehouse) in sorted(iwb_map):
        qty_dict = iwb_map[(company, item, warehouse)]
        if (qty_dict.bal_qty > 0 ):
            data.append([item, item_map[item]["item_name"],
                item_map[item]["item_group"],warehouse,
                item_map[item]["stock_uom"],
                qty_dict.bal_qty,qty_dict.bal_val*1.1,
                qty_dict.opening_qty,qty_dict.opening_val*1.1,
                qty_dict.in_qty,qty_dict.in_val*1.1,
                qty_dict.out_qty,qty_dict.out_val*1.1,
                qty_dict.val_rate*1.1,
                company,item_map[item]["brand"],item_map[item]["description"],
            ])

    return columns, data

def get_columns():
    """return columns"""

    columns = [
        _("Item")+":Link/Item:70",
        _("Item Name")+"::120",
        _("Item Group")+"::80",
        _("Warehouse")+":Link/Warehouse:100",
        _("Stock UOM")+":Link/UOM:50",
        _("Balance Qty")+":Float:80",
        _("Balance Value")+":Float:80",
        _("Opening Qty")+":Float:80",
        _("Opening Value")+":Float:80",
        _("In Qty")+":Float:80",
        _("In Value")+":Float:80",
        _("Out Qty")+":Float:80",
        _("Out Value")+":Float:80",
        _("Valuation Rate")+":Float:90",
        _("Company")+":Link/Company:100",
        _("Brand")+"::90",
        _("Description")+"::140"
    ]

    return columns

def get_conditions(filters):
    conditions = ""
    if not filters.get("from_date"):
        frappe.throw(_("'From Date' is required"))

    if filters.get("to_date"):
        conditions += " and posting_date <= '%s'" % frappe.db.escape(filters["to_date"])
    else:
        frappe.throw(_("'To Date' is required"))

    if filters.get("item_code"):
        conditions += " and item_code = '%s'" % frappe.db.escape(filters.get("item_code"), percent=False)

    if filters.get("warehouse"):
        conditions += " and warehouse = '%s'" % frappe.db.escape(filters.get("warehouse"), percent=False)

    return conditions

def get_stock_ledger_entries(filters):
    conditions = get_conditions(filters)
    return frappe.db.sql("""select item_code, warehouse, posting_date, actual_qty, valuation_rate,
            company, voucher_type, qty_after_transaction, stock_value_difference
        from `tabStock Ledger Entry` force index (posting_sort_index)
        where docstatus < 2 %s order by posting_date, posting_time, name""" %
        conditions, as_dict=1)

def get_item_warehouse_map(filters):
    iwb_map = {}
    from_date = getdate(filters.get("from_date"))
    to_date = getdate(filters.get("to_date"))

    sle = get_stock_ledger_entries(filters)

    for d in sle:
        key = (d.company, d.item_code, d.warehouse)
        if key not in iwb_map:
            iwb_map[key] = frappe._dict({
                "opening_qty": 0.0, "opening_val": 0.0,
                "in_qty": 0.0, "in_val": 0.0,
                "out_qty": 0.0, "out_val": 0.0,
                "bal_qty": 0.0, "bal_val": 0.0,
                "val_rate": 0.0, "uom": None
            })

        qty_dict = iwb_map[(d.company, d.item_code, d.warehouse)]

        if d.voucher_type == "Stock Reconciliation":
            qty_diff = flt(d.qty_after_transaction) - qty_dict.bal_qty
        else:
            qty_diff = flt(d.actual_qty)

        value_diff = flt(d.stock_value_difference)

        if d.posting_date < from_date:
            qty_dict.opening_qty += qty_diff
            qty_dict.opening_val += value_diff

        elif d.posting_date >= from_date and d.posting_date <= to_date:
            if qty_diff > 0:
                qty_dict.in_qty += qty_diff
                qty_dict.in_val += value_diff
            else:
                qty_dict.out_qty += abs(qty_diff)
                qty_dict.out_val += abs(value_diff)

        qty_dict.val_rate = d.valuation_rate
        qty_dict.bal_qty += qty_diff
        qty_dict.bal_val += value_diff

    return iwb_map

def get_item_details(filters):
    condition = ''
    value = ()
    if filters.get("item_code"):
        condition = "where item_code=%s"
        value = (filters["item_code"],)

    items = frappe.db.sql("""select name, item_name, stock_uom, item_group, brand, description
        from tabItem {condition}""".format(condition=condition), value, as_dict=1)

    return dict((d.name, d) for d in items)

def validate_filters(filters):
    if not (filters.get("item_code") or filters.get("warehouse")):
        sle_count = flt(frappe.db.sql("""select count(name) from `tabStock Ledger Entry`""")[0][0])
        if sle_count > 500000:
            frappe.throw(_("Please set filter based on Item or Warehouse"))
