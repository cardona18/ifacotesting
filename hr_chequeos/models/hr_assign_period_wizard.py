# -*- coding: utf-8 -*-
# © <2017> <Omar Torres Silva (otorresgi18@gmail.com)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api

class hr_assign_period_wizard(models.TransientModel):
    _name = 'hr.assign.period.wizard'
    _description = 'HR ASSIGN PERIOD WIZARD'

    period_id = fields.Many2one(
        string='Periodo',
        comodel_name='hr.work.period'
    )
    from_date = fields.Date(
        string='Desde'
    )
    to_date = fields.Date(
        string='Hasta'
    )

    @api.multi
    def relate_worked_days(self):

        days = self.env['hr.timecheck.workday'].search([
            ('start_date', '>=', self.from_date),
            ('start_date', '<=', self.to_date)
        ])

        for day in days:
            day.calc_workedtime()
            day.period_id = self.period_id.id