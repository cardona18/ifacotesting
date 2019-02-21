# -*- coding: utf-8 -*-
# © <2018> <Omar Torres Silva (otorres@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api

class stock_production_lot_gi(models.Model):
    """ Add make date to stock.production.lot model
    """

    _inherit = 'stock.production.lot'


    make_date = fields.Date(
        string='Fecha de fabricación'
    )

