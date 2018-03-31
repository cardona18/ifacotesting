# -*- coding: utf-8 -*-
# © <2017> <Omar Torres Silva (otorresgi18@gmail.com)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime, timedelta
import logging
import math

from openerp import fields, models, api
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class hr_timecheck_workday(models.Model):
    _name = 'hr.timecheck.workday'
    _description = 'HR TIMECHECK WORKDAY'

    name = fields.Char(
        string='ID',
        size=20
    )
    employee_id = fields.Many2one(
        string='Empleado',
        comodel_name='hr.employee'
    )
    company_id = fields.Many2one(
        string='Empresa',
        comodel_name='res.company',
        related='employee_id.company_id'
    )
    turn_id = fields.Many2one(
        string='Turno',
        comodel_name='hr.timecheck.turn'
    )
    check_ids = fields.One2many(
        string='Registros',
        comodel_name='hr.timecheck',
        inverse_name='workday_id'
    )
    worked_hours = fields.Float(
        string='Horas trabajadas',
        default=0.0,
        digits=(16, 2)
    )
    extra_hours = fields.Float(
        string='Horas extra',
        default=0.0,
        digits=(16, 2)
    )
    period_id = fields.Many2one(
        string='Periodo',
        comodel_name='hr.work.period'
    )
    state = fields.Selection(
        string='Estado',
        size=1,
        default='N',
        selection=[
            ('N', 'Nueva'),
            ('P', 'Procesada')
        ]
    )
    start_date = fields.Date(
        string='Fecha'
    )


    @api.model
    def create(self, vals):

        rec = super(hr_timecheck_workday, self).create(vals)

        rec.sudo().write({
            'name': 'WD-%s' % str(rec.id).zfill(6)
        })

        return rec

    @api.multi
    def write(self, vals):

        return super(hr_timecheck_workday, self).write(vals)

    # INIT VALUES
    _MAX_CHECKS_COUNT = 6
    _CHECKS_COUNT = 4
    _MIN_CHECKS_COUNT = 2
    _UTC_DIFF = timedelta(hours=5)

    @api.multi
    def calc_workedtime(self):

        # FORMAT CHECKS
        real_checks = {}
        turn_checks = self.turn_id.get_checks(self.start_date)

        for check in self.check_ids:
            real_checks[check.name] = datetime.strptime(check.check_time, DEFAULT_SERVER_DATETIME_FORMAT) - self._UTC_DIFF

        # CHECK SIZE
        if len(real_checks) != len(turn_checks):
            raise UserError('El número de registros no coincide con el turno {0}'.format(self.name))

        checks = self._sync_checks(turn_checks, real_checks)
        checks_size = len(checks)

        if not real_checks:
            raise UserError('No se pudieron procesar los registros {0}'.format(self.name))

        if checks_size == self._MIN_CHECKS_COUNT:
            self.worked_hours = self.time_diff(checks[0], checks[1], 3600.0)
            self.extra_hours = int(self.time_diff(real_checks['1'], checks[0])) / 3600 + int(self.time_diff(checks[1], real_checks['2'])) / 3600

        if checks_size == self._CHECKS_COUNT:

            break_time = max(self.time_diff(turn_checks['2'], turn_checks['3']),  self.time_diff(checks[1], checks[2])) / 3600.0
            total_hours = self.time_diff(checks[0], checks[3], 3600.0)

            self.worked_hours = total_hours - break_time
            self.extra_hours = int(self.time_diff(real_checks['1'], checks[0])) / 3600 + int(self.time_diff(checks[3], real_checks['4'])) / 3600

        if checks_size == self._MAX_CHECKS_COUNT:

            break_time = max(self.time_diff(turn_checks['2'], turn_checks['3']),  self.time_diff(checks[1], checks[2])) / 3600.0
            total_hours = self.time_diff(checks[0], checks[3], 3600.0)
            permit_hours = self.time_diff(checks[4], checks[5], 3600.0)

            self.worked_hours = total_hours - (break_time + permit_hours)
            self.extra_hours = int(self.time_diff(real_checks['1'], checks[0])) / 3600 + int(self.time_diff(checks[3], real_checks['6'])) / 3600

    def _sync_checks(self, turn_checks, real_checks):

            # CHECK PERMITS
            self.env.cr.execute("""
                SELECT id
                FROM hr_leave_request
                WHERE employee_id = {0}
                AND state = 'OK'
                AND (from_time - '5 hours'::interval)::date >= '{1}'
                AND (to_time - '5 hours'::interval)::date <= '{1}'
            """.format(self.employee_id.id, self.start_date))

            permit_id = self.env.cr.fetchone()

            if not permit_id:

                return [
                    max(real_checks['1'], turn_checks['1']),
                    max(real_checks['2'], turn_checks['2']),
                    max(real_checks['3'], turn_checks['3']),
                    min(real_checks['4'], turn_checks['4'])
                ]

            permit = self.env['hr.leave.request'].browse(permit_id[0])
            permit_from = datetime.strptime(permit.from_time, DEFAULT_SERVER_DATETIME_FORMAT) - self._UTC_DIFF if permit.from_time else False
            permit_to = datetime.strptime(permit.to_time, DEFAULT_SERVER_DATETIME_FORMAT) - self._UTC_DIFF if permit.to_time else False

            if permit.ltype == '01':

                if permit_from < turn_checks['2']:

                    return [
                        max(real_checks['1'], permit_from),
                        max(real_checks['2'], turn_checks['2']),
                        max(real_checks['3'], turn_checks['3']),
                        min(real_checks['4'], turn_checks['4'])
                    ]

                if permit_from > turn_checks['3']:

                    return [
                        max(permit_from, turn_checks['3']),
                        max(real_checks['4'], turn_checks['4'])
                    ]

            if permit.ltype == '02':

                if permit_to > turn_checks['3']:

                    return [
                        max(real_checks['1'], turn_checks['1']),
                        max(real_checks['2'], turn_checks['2']),
                        max(real_checks['3'], turn_checks['3']),
                        min(permit_to, turn_checks['4'])
                    ]

                if permit_to < turn_checks['2']:

                    return [
                        max(real_checks['1'], turn_checks['1']),
                        min(real_checks['2'], permit_to)
                    ]

            if permit.ltype == '03':

                checks_len = len(real_checks)

                if checks_len != self._MAX_CHECKS_COUNT:
                    raise UserError('Se esperaban {0} registros {1} encontrados'.format(self._MAX_CHECKS_COUNT, checks_len))

                if permit_from < turn_checks['2'] and permit_to < turn_checks['2']:

                    return [
                        max(real_checks['1'], turn_checks['1']),
                        max(real_checks['2'], permit_from),
                        max(real_checks['3'], permit_to),
                        max(real_checks['4'], turn_checks['2']),
                        max(real_checks['5'], turn_checks['3']),
                        min(real_checks['6'], turn_checks['4'])
                    ]

                if permit_from > turn_checks['3'] and permit_to > turn_checks['3']:

                    return [
                        max(real_checks['1'], turn_checks['1']),
                        max(real_checks['2'], turn_checks['2']),
                        max(real_checks['3'], turn_checks['3']),
                        max(real_checks['4'], permit_from),
                        max(real_checks['5'], permit_to),
                        min(real_checks['6'], turn_checks['6'])
                    ]

                if permit_from < turn_checks['2'] and permit_to > turn_checks['3']:

                    return [
                        max(real_checks['1'], turn_checks['1']),
                        max(real_checks['2'], turn_checks['2']),
                        max(real_checks['3'], turn_checks['3']),
                        max(real_checks['4'], permit_from),
                        max(real_checks['5'], permit_to),
                        min(real_checks['6'], turn_checks['6'])
                    ]

            return False

    def time_diff(self, from_time, to_time, div_factor = False):

        seconds_diff = (to_time - from_time).total_seconds()

        if div_factor:
            return seconds_diff / div_factor

        return seconds_diff

    def timezone_diff(self, time_obj, interval, add = False):
        return time_obj + interval if add else time_obj - interval