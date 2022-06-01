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
        {"label": _("Liefers-Nr.:"), "fieldname": "delivery_note", "fieldtype": "Link", "options": "Delivery Note", "width": 100},
        {"label": _("Datum - Zeit"), "fieldname": "zeit", "fieldtype": "Time", "width": 140},
        {"label": _("Relation"), "fieldname": "relation", "fieldtype": "Data", "width": 400},
        {"label": _("Container Grosse"), "fieldname": "container_size", "fieldtype": "Data", "width": 200},
        {"label": _("Fzg"), "fieldname": "supplier", "fieldtype": "Data", "width": 400},
    ]

def get_data(filters):
    if type(filters) is str:
        filters = ast.literal_eval(filters)
    else:
        filters = dict(filters)
    
    conditions = ""
    if 'delivery_note' in filters:
        conditions = """ AND `dn`.`name` = "{delivery_note}" """.format(delivery_note=filters['delivery_note'])
    if 'from_date' in filters and filters['from_date']:
        conditions += """ AND (`dn`.`gestellungsdatum` >= '{from_date}' OR `dn`.`gestellungsdatum` IS NULL)""".format(from_date=filters['from_date'])
    if 'to_date' in filters and filters['to_date']:
        conditions += """ AND (`dn`.`gestellungsdatum` <= '{to_date}' OR `dn`.`gestellungsdatum` IS NULL)""".format(to_date=filters['to_date'])
    if 'customer' in filters:
        conditions = """ AND `dn`.`customer` = "{customer}" """.format(customer=filters['customer'])
        
    # prepare query
    sql_query = """
        SELECT
            `base_doc`.`name` AS `delivery_note`,
            `base_doc`.`gestellungsdatum` AS `zeit`,
            `base_doc`.`relation` AS `relation`,
            `base_doc`.`container_size` AS `container_size`,
            `base_doc`.`supplier` AS `supplier`
        FROM (
            SELECT
                `dn`.`name`,
                `dn`.`customer_name`,
                `dn`.`gestellungsdatum`,
                `dn`.`relation`,
                `dn`.`container_size`,
                IF (("FL 30042" | "FL 33969" | "FL 38141" | "FL 39228") = `dn`.`truck`, "Holtkemper", `sup`.`supplier_name`) AS `supplier`,
                (
                    SELECT `against_sales_order`
                    FROM `tabDelivery Note Item` AS `dni`
                    WHERE `dni`.`parent` = `dn`.`name`
                    AND `dni`.`against_sales_order` IS NOT NULL
                    LIMIT 1
                ) AS `sales_order`,
                (
                    SELECT DISTINCT
                        `parent` AS `sinv`
                    FROM `tabSales Invoice Item`
                    WHERE `delivery_note` = `dn`.`name`
                    AND `docstatus` <= 1
                ) AS `sinv`
                
            FROM `tabDelivery Note` AS `dn`
            LEFT JOIN `tabSupplier` AS `sup` ON `dn`.`supplier` = `sup`.`name`
            LEFT JOIN `tabPurchase Order` AS `po` ON `dn`.`name` = `po`.`delivery_note`
            WHERE `dn`.`docstatus` <= 1
                {conditions}
        ) AS `base_doc`
        ORDER BY `base_doc`.`gestellungsdatum` ASC
      """.format(conditions=conditions)
    #frappe.throw(sql_query)
    _data = frappe.db.sql(sql_query, as_dict=1)

    # add totals
    totals = { 'erloes': 0, }
    #for row in _data:
        #row['erloes'] = round(float(row['fremd']) - float(row['aufwand']), 2)
    
    return _data
