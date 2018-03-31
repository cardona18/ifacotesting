# -*- coding: utf-8 -*-
# © <2016> <Omar Torres Silva (otorres@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models

class hr_business_segment(models.Model):
    _name = 'hr.business.segment'
    _description = 'HR BUSINESS SEGMENT'

    name = fields.Char(
        string='Nombre',
        required=True
    )
    code = fields.Char(
        string='Clave'
    )
    old_id = fields.Integer(
        string='Old id',
        index=True
    )