# -*- coding: utf-8 -*-
# © <2017> < ()>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api

class siagi_invoice_line(models.TransientModel):
    _name = 'siagi.invoice.line'
    _description = 'SIAGI INVOICE LINE'

    wizard_id = fields.Many2one(
        string='Wizard',
        comodel_name='siagi.invoice.wizard'
    )
    name = fields.Char(
        string='Factura'
    )
    itype = fields.Selection(
        string='Tipo',
        default='F',
        size=1,
        selection=[
            ('F', 'Factura'),
            ('N', 'Nota de crédito')
        ]
    )
    invoice_date = fields.Date(
        string='Fecha'
    )


