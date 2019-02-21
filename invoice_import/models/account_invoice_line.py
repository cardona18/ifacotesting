# -*- coding: utf-8 -*-
# © <2016> <Omar Torres Silva (otorres@grupoifaco.com.mx) >
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from math import ceil, floor

from odoo import fields, models, api

_logger = logging.getLogger(__name__)

class account_invoice_line_gi(models.Model):
    _inherit = 'account.invoice.line'

    import_line_annex = fields.Text(
        string='Complemento'
    )
    product_cbss = fields.Char(
        string='CBSS',
        size=40
    )
    product_uom_cfdi = fields.Char(
        string='Unidad CFDI',
        size=80
    )
    shipment_num = fields.Char(
        string='Pedimento',
        size=50
    )
    predial_account = fields.Char(
        string='Cuenta predial',
        size=150
    )

    def invoice_line_amount(self, qty, price):

        return self.monetary_round(qty * price, 2)

    def monetary_round(self, num, places = 0):

        dec_diff = str(num - int(num))
        dec_diff = dec_diff[:places + 3]

        if dec_diff[-1:] == '5':
            round_diff = float('0.%s1' % ('0' * places))
            return round(num + round_diff, places)

        return round(num, places)


    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.product_cbss = self.product_id.cbss
            self.product_uom_cfdi = self.product_id.uom_id.name