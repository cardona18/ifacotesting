# -*- coding: utf-8 -*-
# © <2018> <Omar Torres (otorresgi18@gmail.com)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from urllib.parse import quote
import logging

from odoo import fields, models, api

_logger = logging.getLogger(__name__)

class sale_shipping_guide(models.Model):
    _name = 'sale.shipping.guide'
    _description = 'SALE SHIPPING GUIDE'

    name = fields.Char(
        string='Clave'
    )
    shipping_ids = fields.One2many(
        string='Entregas',
        comodel_name='stock.picking',
        inverse_name='shipping_guide_id'
    )
    shippings_count = fields.Integer(
        string='Entregas',
        compute='_shippings_count',
    )
    pending_shippings_count = fields.Integer(
        string='Entregas pendientes',
        compute='_pending_shippings_count',
    )
    send_date = fields.Date(
        string='Envío'
    )
    done_date = fields.Date(
        string='Regreso'
    )
    send_method = fields.Selection(
        string='Medio de embarque',
        size=3,
        default='NTP',
        selection=[
            ('NTP', 'Nuestro trasporte'),
            ('FLE', 'Flete'),
            ('MCL', 'Mismo cliente'),
        ]
    )
    vehicle_id = fields.Many2one(
        string='Vehículo',
        comodel_name='fleet.vehicle'
    )


    def _shippings_count(self):
        """
            Count all stock.shipping.label related records
        """

        self.shippings_count = len(self.sudo().shipping_ids.ids)

    def _pending_shippings_count(self):
        """
            Count all stock.shipping.label related records
        """

        self.pending_shippings_count = self.env['stock.picking'].sudo().search_count([
            ('operation_type', '=', 'outgoing'),
            ('delivery_date', '=', False),
            ('shipping_guide_id', '=', False),
            ('state', '=', 'done'),
            ('sale_id', '!=', False)
        ])

    @api.model
    def create(self, vals):

        vals['name'] = self.env.ref('sales_gi.shipping_guide_sequence').next_by_id()

        res = super(sale_shipping_guide, self).create(vals)

        return res