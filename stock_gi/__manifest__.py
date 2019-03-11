# -*- coding: utf-8 -*-
{
    'name': "STOCK GI",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.odoo.com""",

    'description': """

    """,

    'author': "",
    'website': "",

    # Categories can be used to filter modules in modules listing
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base',
                'stock',
                'quality',
                'purchase_stock'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/stock_picking.xml',
        'views/stock_picking_documents.xml',
        'views/stock_picking_reasons.xml',
        'views/control_tags_printer.xml',
        'views/stock_location.xml',
        'views/stock_move_line.xml',
        'views/stock_scrap.xml',
        'views/stock_inventory.xml',
        'views/stock_backorder_confirmation.xml',
    ]
}
