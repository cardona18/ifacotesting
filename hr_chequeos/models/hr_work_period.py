# -*- coding: utf-8 -*-
# © <2017> <Omar Torres Silva (otorresgi18@gmail.com)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api

class hr_work_period(models.Model):
    _name = 'hr.work.period'
    _description = 'HR WORK PERIOD'

    name = fields.Char(
        string='Nombre',
        required=True
    )
    period_num = fields.Integer(
        string='Número',
        default=1
    )
    from_date = fields.Date(
        string='Desde'
    )
    to_date = fields.Date(
        string='Hasta'
    )
    check_ids = fields.One2many(
        string='Tiempo trabajado',
        comodel_name='hr.timecheck.workday',
        inverse_name='period_id'
    )
    checks_count = fields.Integer(
        string='Tiempo trabajado',
        compute=lambda self: self._checks_count()
    )
    active = fields.Boolean(
        string='Activo',
        default=True
    )
    state = fields.Selection(
        string='Estado',
        size=1,
        default='O',
        selection=[
            ('O', 'Abierto'),
            ('C', 'Cerrado')
        ]
    )

    def _checks_count(self):
        """
            Count all hr.timecheck.workday related records
        """

        self.checks_count = self.check_ids.search_count([('period_id', '=', self.id)])

    @api.multi
    def close_period(self):

        for check_id in self.check_ids:
            check_id.state = 'P'

        self.state = 'C'
        self.active = False