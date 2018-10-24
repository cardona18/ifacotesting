# -*- coding: utf-8 -*-
# © <2018> <Omar Torres (otorresgi18@gmail.com) >
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api

class sale_order_gi(models.Model):
    _inherit = 'sale.order'

    bidding_id = fields.Many2one(
        string='Licitación',
        comodel_name='sale.bidding'
    )