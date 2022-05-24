from __future__ import unicode_literals
from frappe import _

def get_data():
    return[
        {
            "label": _("Selling"),
            "icon": "fa fa-money",
            "items": [
                   {
                       "type": "doctype",
                       "name": "Customer",
                       "label": _("Customer"),
                       "description": _("Customer")
                   },
                   {
                       "type": "doctype",
                       "name": "Sales Order",
                       "label": _("Sales Order"),
                       "description": _("Sales Order")
                   },
                   {
                       "type": "doctype",
                       "name": "Delivery Note",
                       "label": _("Delivery Note"),
                       "description": _("Delivery Note")
                   },
                   {
                       "type": "doctype",
                       "name": "Sales Invoice",
                       "label": _("Sales Invoice"),
                       "description": _("Sales Invoice")
                   },
                   {
                        "type": "doctype",
                        "name": "Purchase Order",
                        "label": _("Purchase Order"),
                        "description": _("Purchase Order")
                   }
            ]
        },
        {
            "label": _("Monitoring"),
            "icon": "fa fa-money",
            "items": [
                   {
                       "type": "report",
                       "name": "Planung",
                       "label": _("Planung"),
                       "doctype": "Delivery Note",
                       "is_query_report": True
                   },
                   {
                        "type": "report",
                        "name": "Auftragsbuch",
                        "label": _("Auftragsbuch"),
                        "doctype": "Sales Order",
                        "is_query_report": True
                   }
            ]
        }
]
