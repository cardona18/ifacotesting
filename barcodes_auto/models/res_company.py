# -*- coding: utf-8 -*-
# © <2017> <Juan Carlos Vazquez Beas (jcvazquez@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import sys, logging
from odoo import fields, models, api

_logger = logging.getLogger(__name__)

class res_company(models.Model):
    """Documentation for a class res_company inherit = 'res.company'.
    Esta clase es heredada para agregar el campo 'Clave para código de barras'.
    """
    _inherit = 'res.company'

    code_ean = fields.Char(
        string='Clave para código de barras',
        size=5, 
    )
