# -*- coding: utf-8 -*-
{
    'name': "Compras GI",

    'summary': """
        Adecuaciones al modulo de compras GI
        """,

    'description': """
        e e j
    """,

    'author': "IACDev (iacdev@grupoifaco.com.mx)",
    'website': "http://www.grupoifaco.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '11.1.1',

    # any module necessary for this one to work correctly
    'depends': ['base','res_partner_gi','hr','hr_org_char','data_filemanager','purchase','stock','mrp_plm','purchase_requisition','stock_gi'],

    # always loaded
    'data': [
        'data/purchases_data.xml',
        'wizards/cancel_purchase_requisition.xml',
        'wizards/input_free_wizard.xml',
        'wizards/purchase_immediate_transfer.xml',
        'views/purchase_reception.xml',
        'views/xml_no_validated.xml',
        'views/product_gi.xml',
        'views/hr_employee.xml',
        'views/purchase_order_form.xml',
        'views/res_partner.xml',
        'views/hr_department.xml',
        'views/purchase_requisition.xml',
        'views/template/purchase_requisition_template.xml',   
        'views/purchase_order_line.xml',
        'views/purchase_requisition_line.xml',
        'views/boarding_ways.xml',
        'views/purchase_consignee.xml',
        'views/delivery_addresses.xml',
        'views/import_licenses.xml',
        'views/account_invoice.xml',
        'views/use_cfdi.xml',
        'views/stock_overprocessed_transfer.xml',
        'views/template/purchase_order_templates.xml',
        'views/template/purchase_quotation_templates.xml',
        'views/template/purchase_order_templates_english.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
    ]
}
