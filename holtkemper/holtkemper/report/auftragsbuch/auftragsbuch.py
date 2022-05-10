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
        {"label": _("Position Nr."), "fieldname": "po_no", "fieldtype": "Data", "width": 110},
        {"label": _("Beleg Datum"), "fieldname": "sales_order_date", "fieldtype": "Date", "width": 90},
        {"label": _("Belegsumme"), "fieldname": "base_grand_total", "fieldtype": "Currency", "width": 120},
        {"label": _("Rechg-Nr.:"), "fieldname": "sales_invoice", "fieldtype": "Link", "options": "Sales Invoice", "width": 85},
        {"label": _("Liefers-Nr.:"), "fieldname": "delivery_note", "fieldtype": "Link", "options": "Delivery Note", "width": 85},
        {"label": _("Empfänger"), "fieldname": "customer_name", "fieldtype": "Data", "width": 150},
        {"label": _("Relation"), "fieldname": "relation", "fieldtype": "Data", "width": 150},
        {"label": _("Datum"), "fieldname": "gestellungsdatum", "fieldtype": "Date", "width": 60},
        {"label": _("Sub"), "fieldname": "supplier", "fieldtype": "Data", "width": 130},
        {"label": _("FL 30042"), "fieldname": "fl30042", "fieldtype": "Data", "width": 85},
        {"label": _("FL 33969"), "fieldname": "fl33969", "fieldtype": "Data", "width": 85},
        {"label": _("FL 38141"), "fieldname": "fl38141", "fieldtype": "Data", "width": 85},
        {"label": _("FL 39228"), "fieldname": "fl39228", "fieldtype": "Data", "width": 85},
        {"label": _("offen"), "fieldname": "offen", "fieldtype": "Data", "width": 85},
        {"label": _("Fremd"), "fieldname": "fremd", "fieldtype": "Data", "width": 85},
        {"label": _("Aufwand"), "fieldname": "aufwand", "fieldtype": "Data", "width": 85},
        {"label": _("Erlös in CHF"), "fieldname": "erloes", "fieldtype": "Data", "width": 85},
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
            `tabSales Order`.`po_no` AS `po_no`,
            `tabSales Order`.`transaction_date` AS `sales_order_date`,
            `tabDelivery Note`.`base_grand_total` AS `base_grand_total`,
            `tabSales Invoice Item`.`parent` AS `sales_invoice`,
            `tabDelivery Note`.`name` AS `delivery_note`,
            `tabSales Order`.`customer_name` AS `customer_name`,
            `tabSales Invoice`.`relation` AS `relation`,
            `tabSales Order`.`gestellungsdatum` AS `gestellungsdatum`,
            IF (("FL 30042" | "FL 33969" | "FL 38141" | "FL 39228") = `tabDelivery Note`.`truck`, "Holtkemper", `tabSupplier`.`supplier_name`) AS `supplier`,
            IF (`tabDelivery Note`.`truck` = "FL30042", `tabDelivery Note`.`base_grand_total`, 0) AS `fl30042`,
            IF (`tabDelivery Note`.`truck` = "FL33969", `tabDelivery Note`.`base_grand_total`, 0) AS `fl33969`,
            IF (`tabDelivery Note`.`truck` = "FL38141", `tabDelivery Note`.`base_grand_total`, 0) AS `fl38141`,
            IF (`tabDelivery Note`.`truck` = "FL39228", `tabDelivery Note`.`base_grand_total`, 0) AS `fl39228`,
            IF (`tabSales Invoice`.`status` =  "Completed", 0, IFNULL(`tabSales Invoice`.`outstanding_amount`, 0)) AS `offen`,
            IF (`tabDelivery Note`.`supplier` =  `tabSupplier`.`name`, IFNULL(`tabDelivery Note`.`base_grand_total`, 0), 0) AS `fremd`,
            IF (`tabDelivery Note`.`name` =  `tabPurchase Order`.`delivery_note`, IFNULL(`tabPurchase Order`.`total`, 0), 0) AS `aufwand`,
            NULL AS `erloes`
        FROM `tabSales Order`
        LEFT JOIN `tabSales Invoice Item` ON `tabSales Order`.`name` = `tabSales Invoice Item`.`sales_order` AND `tabSales Invoice Item`.`docstatus` < 2
        LEFT JOIN `tabSales Invoice` ON `tabSales Invoice`.`name` = `tabSales Invoice Item`.`parent` AND `tabSales Invoice`.`docstatus` < 2
        LEFT JOIN `tabDelivery Note Item` ON `tabSales Order`.`name` = `tabDelivery Note Item`.`against_sales_order` 
        LEFT JOIN `tabDelivery Note` ON `tabDelivery Note`.`name` = `tabDelivery Note Item`.`parent`
        LEFT JOIN `tabSupplier` ON `tabDelivery Note`.`supplier` = `tabSupplier`.`name`
        LEFT JOIN `tabPurchase Order` ON `tabDelivery Note`.`name` = `tabPurchase Order`.`delivery_note` 
        WHERE
            `tabSales Order`.`docstatus` = 1
            {conditions}
        GROUP BY `tabDelivery Note`.`name`
      """.format(conditions=conditions)
    #frappe.throw(sql_query)
    data = frappe.db.sql(sql_query, as_dict=1)

    # add totals
    totals = {'base_grand_total': 0, 'fl30042': 0, 'fl33969': 0, 'fl38141': 0, 'fl39228': 0, 'offen': 0, 'fremd': 0, 'aufwand': 0, 'erloes': 0, }
    for row in data:
        row['erloes'] = round(float(row['fremd']) - float(row['aufwand']), 2)
        totals['base_grand_total'] += row['base_grand_total']
        totals['fl30042'] += row['fl30042']
        totals['fl33969'] += row['fl33969']
        totals['fl38141'] += row['fl38141']
        totals['fl39228'] += row['fl39228']
        totals['offen'] += row['offen']
        totals['fremd'] += row['fremd']
        totals['aufwand'] += row['aufwand']
        totals['erloes'] += round(row['erloes'])
    data.append(totals)
    
    return data
