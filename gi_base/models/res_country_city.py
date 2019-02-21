# -*- coding: utf-8 -*-
# © <2016> <Omar Torres Silva (otorres@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models

class res_country_city(models.Model):
    _name = 'res.country.city'
    _description = 'RES COUNTRY CITY'

    name = fields.Char(
        string='Nombre',
        required=True
    )
    short_name = fields.Char(
        string='Abreviatura'
    )
    state_id = fields.Many2one(
        string='Estado',
        comodel_name='res.country.state',
        ondelete='cascade'
    )
    old_id = fields.Integer(
        string='Clave'
    )