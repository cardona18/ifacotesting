# -*- coding: utf-8 -*-
# © <2016> <Omar Torres Silva (otorres@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models

class cfdi_town(models.Model):
    _name = 'cfdi.town'
    _description = 'CFDI TOWN'

    name = fields.Char(
        string='Nombre'
    )
    code = fields.Char(
        string='Clave',
        size=3
    )
    zip_code = fields.Char(
        string='Código postal',
        size=5
    )
    state_id = fields.Many2one(
        string='Estado',
        comodel_name='res.country.state'
    )
