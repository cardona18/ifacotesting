# -*- coding: utf-8 -*-
# © <2018> <Omar Torres (otorresgi18@gmail.com)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime

from odoo import fields, models, api

class sale_bidding(models.Model):
    _name = 'sale.bidding'
    _description = 'SALE BIDDING'

    name = fields.Char(
        string='Nombre',
        required=True
    )
    date = fields.Date(
        string='Fecha',
        default=datetime.today()
    )
    agent_id = fields.Many2one(
        string='Representante',
        comodel_name='res.users'
    )
    orders_count = fields.Integer(
        string='Pedidos',
        compute='_orders_count',
    )
    order_ids = fields.One2many(
        string='Pedidos',
        comodel_name='sale.order',
        inverse_name='bidding_id'
    )
    description = fields.Text(
        string='Descripción'
    )

    def _orders_count(self):

        for item in self:
            item.orders_count = len(item.sudo().order_ids)