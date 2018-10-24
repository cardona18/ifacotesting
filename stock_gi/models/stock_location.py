# -*- coding: utf-8 -*-
# © <2016> <Juan Carlos Vazquez Beas (jcvazquez@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api

class stock_location(models.Model):
    _inherit = 'stock.location'

    check_tags = fields.Boolean(
        string='Crear etiquetas',
    )
    get_lot = fields.Boolean(
        string='Exigir lote de proveedor',
    )
