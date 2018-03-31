# -*- coding: utf-8 -*-
# © <2017> <Omar Torres Silva (otorresgi18@gmail.com)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime

from openerp import fields, models
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT

class hr_public_holiday(models.Model):
    _name = 'hr.public.holiday'
    _description = 'HR PUBLIC HOLIDAY'

    name = fields.Char(
        string='Nombre',
        required=True
    )
    holiday_date = fields.Date(
        string='Fecha',
        required=True
    )
    current_year_date = fields.Date(
        string='Año actual',
        compute=lambda self: self._compute_current_year_date()
    )
    all_day = fields.Boolean(
        string='Todo el día',
        default=True
    )
    category_id = fields.Many2one(
        string='Categoría',
        comodel_name='hr.public.holiday.category'
    )

    def _compute_current_year_date(self):

        for item in self:
            from_date = datetime.strptime(item.holiday_date, DEFAULT_SERVER_DATE_FORMAT)
            item.current_year_date = from_date.replace(year=datetime.today().year)