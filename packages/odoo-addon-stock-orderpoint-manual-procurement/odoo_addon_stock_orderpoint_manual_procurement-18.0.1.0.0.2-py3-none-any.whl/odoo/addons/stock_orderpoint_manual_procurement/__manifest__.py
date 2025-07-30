# Copyright 2016-20 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Stock Orderpoint Manual Procurement",
    "summary": "Allows to create procurement orders from orderpoints instead "
    "of relying only on the scheduler.",
    "version": "18.0.1.0.0",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-orderpoint",
    "category": "Warehouse Management",
    "depends": ["purchase_stock"],
    "demo": ["demo/product.xml"],
    "data": [
        "security/ir.model.access.csv",
        "security/stock_orderpoint_manual_procurement_security.xml",
        "wizards/make_procurement_orderpoint_view.xml",
        "views/stock_warehouse_orderpoint_view.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "stock_orderpoint_manual_procurement/static/src/views/stock_orderpoint_list_view.xml",
            "stock_orderpoint_manual_procurement/static/src/views/stock_orderpoint_list_view.esm.js",
        ],
    },
    "license": "AGPL-3",
    "installable": True,
    "application": False,
}
