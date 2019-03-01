# -*- coding: utf-8 -*-
{
    'name': "Ventas Grupo IFACO",

    'summary': """Adecuación al módulo de ventas para la operación interna""",

    'description': """

    """,

    'author': "Omar Torres Silva (otorresgi18@gmail.com)",
    'website': "http://www.grupoifaco.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Sales Management',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'crm',
        'sale_management',
        'sales_team',
        'sale_mrp',
        'product_make',
        'product_expiry',
        'l10n_mx_edi',
        'fleet',
        'res_partner_gi',
        'product_gi',
        'legal_technical',
        'ireport_custom',
        'quality_manager_gi'
    ],

    # always loaded
    'data': [
        'security/security.xml',
        'data/shipment_cfdi.xml',
        'wizards/sale_shipping_guide_wizard.xml',
        'wizards/sale_bidding_codes_wizard.xml',
        'views/sales_gi_main.xml',
        'views/stock_shipping_label.xml',
        'views/stock_picking.xml',
        'views/res_partner.xml',
        'views/account_invoice.xml',
        'views/sale_bidding.xml',
        'views/sale_shipping_guide.xml',
        'views/sale_order.xml',
        'security/ir.model.access.csv',
    ]
}
