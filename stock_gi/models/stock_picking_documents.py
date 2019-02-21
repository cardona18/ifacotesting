# -*- coding: utf-8 -*-
# © <2017> <Juan Carlos Vazquez Beas (jcvazquez@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api

class stock_picking_documents(models.Model):
    _name = 'stock.picking.documents'

    name = fields.Char(
        string='Documento',
        required=True
    )
