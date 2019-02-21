# -*- coding: utf-8 -*-
# © <2017> <Juan Carlos Vazquez Beas (jcvazquez@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import fields, models, api

class res_partner_gi(models.Model):
    _inherit = 'res.partner'

    curp = fields.Char(
        string='CURP',
        size=30
    )
    customer = fields.Boolean(
        default=False
    )