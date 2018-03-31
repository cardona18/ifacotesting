# -*- coding: utf-8 -*-
# © <2017> <Omar Torres Silva (otorresgi18@gmail.com)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from openerp import fields, models, api

_logger = logging.getLogger(__name__)

class hr_worktime_wizard(models.TransientModel):
    _name = 'hr.worktime.wizard'
    _description = 'HR WORKTIME WIZARD'

    period_id = fields.Many2one(
        string='Periodo',
        comodel_name='hr.work.period'
    )
    export_type = fields.Selection(
        string='Tipo',
        default='PR',
        size=2,
        required=True,
        selection=[
            ('PR', 'Vista previa'),
            ('SH', 'Hoja de cálculo'),
            ('PS', 'Entradas programadas')
        ]
    )

    @api.multi
    def export_time(self):

        # RE-CALC WORKED TIME
        for check in self.check_ids:
            check.calc_workedtime()

        return {
            'type' : 'ir.actions.act_url',
            'url': '/web/export_time/timechecks?pid=%s&type=%s' % (self.period_id.id, self.export_type),
            'target': 'new'
        }