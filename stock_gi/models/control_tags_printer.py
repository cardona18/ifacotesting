# -*- coding: utf-8 -*-
# © <2016> <Juan Carlos Vazquez Beas (jcvazquez@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api

class control_tags(models.Model):
    _name = 'control.tags.printer'

    name = fields.Many2one(
        'stock.production.lot',
        string='Entrada',
        required=True,
    )
    name_char = fields.Char(
        string='Entrada nombre',
        required=True,
    )
    company_id = fields.Char(
        string='Compañía',
        required=True,
    )
    lot_sup = fields.Char(
        string='Número de lote',
        required=True
    )
    product_id = fields.Char(
        string='Producto',
        required=True
    )
    default_code = fields.Char(
        string='Referencia interna',
        required=True
    )
    type_date = fields.Char(
        string='Tipo de vigencia',
        required=True
    )
    life_date = fields.Datetime(
        string='Fecha de vigencia',
        required=True
    )
    num_container = fields.Integer(
        string='Número de contenedores',
    )
    user_printer = fields.Char(
        string='Usuario que imprimió'
    )
    printer = fields.Boolean(
        string='Impreso',
    )

