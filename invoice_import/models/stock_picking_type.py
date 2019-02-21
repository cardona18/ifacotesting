# -*- coding: utf-8 -*-
# © <2018> < ()>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api

class stock_picking_type(models.Model):
    _inherit = 'stock.picking.type'

    transfer = fields.Boolean(
        string='Es un traslado',
    )
