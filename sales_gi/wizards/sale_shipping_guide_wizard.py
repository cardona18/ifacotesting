# -*- coding: utf-8 -*-
# © <2018> <Omar Torres (otorresgi18@gmail.com)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import fields, models, api

_logger = logging.getLogger(__name__)

class sale_shipping_guide_wizard(models.TransientModel):
    _name = 'sale.shipping.guide.wizard'
    _description = 'SALE SHIPPING GUIDE WIZARD'

    guide_id = fields.Many2one(
        string='Guía',
        comodel_name='sale.shipping.guide'
    )
    picking_ids = fields.Many2many(
        string='Entregas',
        comodel_name='stock.picking'
    )

    @api.multi
    def relate_shipping_guide(self):

        for picking_id in self.picking_ids:
            picking_id.shipping_guide_id = self.guide_id.id

        return {

            'name':'Guía de embarque',
            'view_type': 'form',
            'view_mode': 'tree',
            'views' : [(self.env.ref('sales_gi.sale_shipping_guide_form').id, 'form')],
            'res_model': 'sale.shipping.guide',
            'view_id': self.env.ref('sales_gi.sale_shipping_guide_form').id,
            'type': 'ir.actions.act_window',
            'res_id': self.guide_id.id,
            'target': 'current',
            'context': self.env.context
        }