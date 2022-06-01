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
        {"label": _("Kunde-Ref."), "fieldname": "po_no", "fieldtype": "Data", "width": 110},
        {"label": _("Beleg Datum"), "fieldname": "sales_order_date", "fieldtype": "Date", "width": 75},
        {"label": _("Belegsumme"), "fieldname": "base_grand_total", "fieldtype": "Currency", "width": 100},
        {"label": _("Rechg-Nr.:"), "fieldname": "sales_invoice", "fieldtype": "Link", "options": "Sales Invoice", "width": 90},
        {"label": _("Liefers-Nr.:"), "fieldname": "delivery_note", "fieldtype": "Link", "options": "Delivery Note", "width": 80},
        {"label": _("Auftrag-Nr.:"), "fieldname": "sales_order", "fieldtype": "Link", "options": "Sales Order", "width": 80},
        {"label": _("Empfänger"), "fieldname": "customer_name", "fieldtype": "Data", "width": 120},
        {"label": _("Relation"), "fieldname": "relation", "fieldtype": "Data", "width": 130},
        {"label": _("Datum"), "fieldname": "gestellungsdatum", "fieldtype": "Date", "width": 60},
        {"label": _("Sub"), "fieldname": "supplier", "fieldtype": "Data", "width": 100},
        {"label": _("FL 30042"), "fieldname": "fl30042", "fieldtype": "Float", "precision": 2, "width": 80},
        {"label": _("FL 33969"), "fieldname": "fl33969", "fieldtype": "Float", "precision": 2,  "width": 80},
        {"label": _("FL 38141"), "fieldname": "fl38141", "fieldtype": "Float", "precision": 2, "width": 80},
        {"label": _("FL 39228"), "fieldname": "fl39228", "fieldtype": "Float", "precision": 2, "width": 80},
        {"label": _("offen"), "fieldname": "offen", "fieldtype": "Float", "precision": 2, "width": 80},
        {"label": _("Fremd"), "fieldname": "fremd", "fieldtype": "Float", "precision": 2, "width": 80},
        {"label": _("Aufwand"), "fieldname": "aufwand", "fieldtype": "Float", "precision": 2, "width": 80},
        {"label": _("Erlös in CHF"), "fieldname": "erloes", "fieldtype": "Currency", "width": 100},
    ]

def get_data(filters):
    if type(filters) is str:
        filters = ast.literal_eval(filters)
    else:
        filters = dict(filters)
    
    conditions = ""
    if 'customer' in filters:
        conditions = """ AND `dn`.`customer` = "{customer}" """.format(customer=filters['customer'])
        
    # prepare query
    sql_query = """
        SELECT
            `base_doc`.`po_no` AS `po_no`,
            `so`.`transaction_date` AS `sales_order_date`,
            `base_doc`.`base_grand_total` AS `base_grand_total`,
            `sinv`.`name` AS `sales_invoice`,
            `base_doc`.`name` AS `delivery_note`,
            `base_doc`.`sales_order` AS `sales_order`,
            `base_doc`.`customer_name` AS `customer_name`,
            `base_doc`.`relation` AS `relation`,
            `base_doc`.`gestellungsdatum` AS `gestellungsdatum`,
            `base_doc`.`supplier` AS `supplier`,
            `base_doc`.`fl30042` AS `fl30042`,
            `base_doc`.`fl33969` AS `fl33969`,
            `base_doc`.`fl38141` AS `fl38141`,
            `base_doc`.`fl39228` AS `fl39228`,
            IF (`sinv`.`status` = 'Completed', 0, `base_doc`.`base_grand_total`) AS `offen`,
            `base_doc`.`fremd` AS `fremd`,
            `base_doc`.`aufwand` AS `aufwand`,
            `base_doc`.`erloes`
        FROM (
            SELECT
                `dn`.`po_no`,
                `dn`.`base_grand_total`,
                `dn`.`name`,
                `dn`.`customer_name`,
                `dn`.`customer`,
                `dn`.`relation`,
                `dn`.`gestellungsdatum`,
                IF (("FL 30042" | "FL 33969" | "FL 38141" | "FL 39228") = `dn`.`truck`, "Holtkemper", `sup`.`supplier_name`) AS `supplier`,
                IF (`dn`.`truck` = "FL30042", `dn`.`base_grand_total`, 0) AS `fl30042`,
                IF (`dn`.`truck` = "FL33969", `dn`.`base_grand_total`, 0) AS `fl33969`,
                IF (`dn`.`truck` = "FL38141", `dn`.`base_grand_total`, 0) AS `fl38141`,
                IF (`dn`.`truck` = "FL39228", `dn`.`base_grand_total`, 0) AS `fl39228`,
                IF ((`dn`.`supplier` IS NULL ) OR (`dn`.`supplier` = ""), 0, IFNULL(`dn`.`base_grand_total`, 0)) AS `fremd`,
                IF (`po`.`delivery_note` IS NOT NULL, IFNULL(`po`.`base_grand_total`, 0), 0) AS `aufwand`,
                NULL AS `erloes`,
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
                    AND `docstatus` = 1
                ) AS `sinv`
                
            FROM `tabDelivery Note` AS `dn`
            LEFT JOIN `tabSupplier` AS `sup` ON `dn`.`supplier` = `sup`.`name`
            LEFT JOIN `tabPurchase Order` AS `po` ON `dn`.`name` = `po`.`delivery_note`
            WHERE `dn`.`docstatus` = 1
                {conditions}
        ) AS `base_doc`
        LEFT JOIN `tabSales Order` AS `so` ON `base_doc`.`sales_order` = `so`.`name`
        LEFT JOIN `tabSales Invoice` AS `sinv` ON `base_doc`.`sinv` = `sinv`.`name`         
      """.format(conditions=conditions)
    #frappe.throw(sql_query)
    _data = frappe.db.sql(sql_query, as_dict=1)

    # add totals
    totals = { 'erloes': 0, }
    for row in _data:
        row['erloes'] = round(float(row['fremd']) - float(row['aufwand']), 2)
    
    return _data
