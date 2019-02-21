# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'EAN Y DUM auto',
    'category': 'Website',
    'version': '1.0',
    'summary': 'Generador de codigos EAN Y DUM',
    'description': """
Odoo Contact Form
====================

        """,
    'depends': ['crm','product','stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_template.xml',
        'views/res_company.xml',
        'views/product_packaging.xml',
        # 'views/product_product.xml',
    ],
    'installable': True,
}
