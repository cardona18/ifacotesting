# -*- coding: utf-8 -*-
{
    'name': "PAYMENT REPORTS GI",

    'summary': """Se agregan nuevos formatos para imprimir cheques en el módulo de facturación """,

    'description': """ El sistema tiene una opción de imprimir cheque  en el menú Compras → Pagos por cada uno de las siguientes plantillas:
        ◦ HSBC 2012
        ◦ Scotiabank May/10
        ◦ Scotiabank Nuevo
        ◦ Formato HSBC
        ◦ HSBC Mainac
    """,

    'author': "Mateo Alexander Zabala Gutierrez (mzabalagutierrez@gmail.com)",
    'website': "https://www.grupoifaco.com.mx/",

    # Categories can be used to filter modules in modules listing
    'category': 'Localization',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account_payment', 'l10n_us_check_printing'],

    # always loaded
    'data': [
        'report/print_HSBC_2012.xml',
        'report/print_Scotiabank_May_10.xml',
        'report/print_Scotiabank_Nuevo.xml',
        'report/print_HSBC.xml',
        'report/print_HSBC_Mainac.xml',
        'views/roles_company.xml',
        'views/no_negociable.xml',
        'views/no_imprimir_cheques.xml',
    ],
    'application': True,
}
