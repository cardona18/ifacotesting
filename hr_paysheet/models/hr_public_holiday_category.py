# -*- coding: utf-8 -*-
# © <2017> <Omar Torres Silva (otorresgi18@gmail.com)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models

class hr_public_holiday_category(models.Model):
    _name = 'hr.public.holiday.category'
    _description = 'HR PUBLIC HOLIDAY CATEGORY'

    name = fields.Char(
        string='Nombre',
        required=True
    )
