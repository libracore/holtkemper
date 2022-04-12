# Copyright (c) 2022, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
import ast

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": _("Position Nr."), "fieldname": "sales_order", "fieldtype": "Link", "options": "Sales Order", "width": 110},
        {"label": _("Beleg Datum"), "fieldname": "sales_order_date", "fieldtype": "Date", "width": 140},
        {"label": _("Belegsumme"), "fieldname": "base_grand_total", "fieldtype": "Currency", "width": 120},        
        {"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 100},
        {"label": _("Customer name"), "fieldname": "customer_name", "fieldtype": "Data", "width": 150}
        
    ]

def get_data(filters):
    if type(filters) is str:
        filters = ast.literal_eval(filters)
    else:
        filters = dict(filters)
    
    conditions = ""
    if 'customer' in filters:
        conditions = """ AND `tabSales Order`.`customer` = "{customer}" """.format(customer=filters['customer'])
        
    # prepare query
    sql_query = """
        SELECT
            `tabSales Order`.`name` AS `sales_order`,
            `tabSales Order`.`transaction_date` AS `sales_order_date`,
            `tabSales Order`.`base_grand_total` AS `base_grand_total`,
            `tabSales Order`.`customer` AS `customer`,
            `tabSales Order`.`customer_name` AS `customer_name`
        FROM `tabSales Order`
        WHERE
            `tabSales Order`.`docstatus` = 1
            {conditions}
      """.format(conditions=conditions)
    
    data = frappe.db.sql(sql_query, as_dict=1)

    # add totals
    totals = {'base_grand_total': 0}
    for row in data:
        totals['base_grand_total'] += row['base_grand_total']
        
    data.append(totals)
    
    return data
