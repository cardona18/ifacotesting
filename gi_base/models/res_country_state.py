# -*- coding: utf-8 -*-
# © <2016> <Omar Torres Silva (otorres@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models

class res_country_state(models.Model):
    _inherit = 'res.country.state'

    old_id = fields.Integer(
        string='Clave'
    )
    key = fields.Char(
        string='Clave de entidad',
        size=2
    )