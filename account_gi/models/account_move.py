# -*- coding: utf-8 -*-
# © <2018> < ()>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging

from odoo import fields, models, api

_logger = logging.getLogger(__name__)


class account_move(models.Model):
    _inherit = 'account.move'

    def _get_c_ecchange(self):
        for self_id in self:
            invoice_id = self.env['account.invoice'].search([('move_id', '=', self_id.id)], limit=1)
            _logger.warning("la vaca lola")
            _logger.warning(invoice_id)
            if invoice_id:
                self_id.c_exchang = invoice_id.c_exchang
                return  invoice_id.c_exchang

    def _get_ecchange(self):
        for self_id in self:
            invoice_id = self.env['account.invoice'].search([('move_id', '=', self_id.id)], limit=1)
            _logger.warning("la vaca lola")
            _logger.warning(invoice_id)
            if invoice_id:
                self_id.exchang = invoice_id.exchang
                return  invoice_id.exchang



    c_exchang = fields.Char(
        string='Tipo de cambio al dia de la orden de compra',
        compute='_get_c_ecchange',

    )
    exchang = fields.Float(
        string='Tipo de cambio',
        compute='_get_ecchange',

    )
