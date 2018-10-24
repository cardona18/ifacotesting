# -*- coding: utf-8 -*-
# © <2018> <Omar Torres (otorresgi18@gmail.com)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from urllib.parse import quote

from odoo import fields, models, api

class stock_shipping_label(models.Model):
    _name = 'stock.shipping.label'
    _description = 'STOCK SHIPPING LABEL'

    name = fields.Char(
        string='Número',
        required=True
    )
    picking_id = fields.Many2one(
        string='Entrega',
        comodel_name='stock.picking'
    )
    labels_total = fields.Integer(
        string='Total'
    )
    code = fields.Char(
        string='Clave',
        size=50
    )
    lot_num = fields.Char(
        string='Lote',
        size=20
    )
    rs_name = fields.Char(
        string='Registro sanitario',
        size=50
    )
    expiration = fields.Char(
        string='Caducidad',
        size=15
    )
    customer = fields.Text(
        string='Cliente'
    )
    dst = fields.Text(
        string='Destino'
    )
    address = fields.Text(
        string='Dirección'
    )
    content = fields.Integer(
        string='Contenido'
    )
    description = fields.Text(
        string='Descripción'
    )