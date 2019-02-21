# -*- coding: utf-8 -*-
# © <2016> <Juan Carlos Vazquez Beas (jcvazquez@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from dateutil import tz
from datetime import datetime
from odoo import fields, models, api
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError


_logger = logging.getLogger(__name__)

class stock_inventory(models.Model):
    _inherit = 'stock.inventory'

    document_id = fields.Many2one(
        'stock.picking.documents',
        string='Documento',
    )
    number = fields.Char(
        string='Numero',
        size=15,
    )
    reason_id = fields.Many2one(
        'stock.picking.reasons',
        string='Motivo',
    )
    description = fields.Text(
        string='Descripción',
    )
   
    @api.multi
    def unlink(self):
        if self.state  != 'draft':
            raise ValidationError('No puedes eliminar el ajuste de inventario por qué ya está validado.')
        else:
            return models.Model.unlink(self)
