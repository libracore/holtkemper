// Copyright (c) 2022, libracore and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Planung"] = {
    "filters": [
        {
            "fieldname": "customer",
            "label": __("Customer"),
            "fieldtype": "Link",
            "options": "Customer"
        },
        {
            "fieldname": "delivery_note",
            "label": __("Delivery Note"),
            "fieldtype": "Link",
            "options": "Delivery Note"
        },
        {
            "fieldname":"from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.add_days(frappe.datetime.get_today(), (-1) * ((new Date().getDay() - 1))),
            "width": "60px"
        },
        {
            "fieldname":"to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.add_days(frappe.datetime.get_today(), (-1) * ((new Date().getDay() - 1)) +6),
            "width": "60px"
        },
    ]
};
