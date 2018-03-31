# -*- coding: utf-8 -*-
# © <2017> <Omar Torres Silva (otorresgi18@gmail.com)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models

class hr_extra_time_request(models.Model):
    _name = 'hr.extra.time.request'
    _description = 'HR EXTRA TIME REQUEST'

    name = fields.Char(
        string='Nombre',
        required=True
    )
