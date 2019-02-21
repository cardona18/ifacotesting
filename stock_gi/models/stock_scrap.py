# -*- coding: utf-8 -*-
# © <2017> <Juan Carlos Vazquez Beas (jcvazquez@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api

class stock_scrap(models.Model):
    _inherit = 'stock.scrap'

    document_id = fields.Many2one(
        'stock.picking.documents',
        string='Documento',
    )
    number = fields.Char(
        string='Numero',
    )
    reason_id = fields.Many2one(
        'stock.picking.reasons',
        string='Motivo',
    )
    description = fields.Text(
        string='Descripción',
    )