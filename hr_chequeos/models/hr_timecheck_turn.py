# -*- coding: utf-8 -*-
# © <2017> <Omar Torres Silva (otorresgi18@gmail.com)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime, timedelta

from openerp import fields, models, api
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT

class hr_timecheck_turn(models.Model):
    _name = 'hr.timecheck.turn'
    _description = 'HR TIMECHECK TURN'

    name = fields.Char(
        string='Nombre'
    )
    start_turn = fields.Float(
        string='Entrada',
        digits=(2, 2)
    )
    has_break = fields.Boolean(
        string='Tiene receso',
        default=False
    )
    start_break = fields.Float(
        string='Inicio receso',
        digits=(2, 2)
    )
    end_break = fields.Float(
        string='Fin receso',
        digits=(2, 2)
    )
    end_turn = fields.Float(
        string='Salida',
        digits=(2, 2)
    )
    hour_mode = fields.Selection(
        string='Modo',
        size=1,
        default='1',
        selection=[
            ('1', 'Normal'),
            ('2', 'Salida al siguiente día')
        ]
    )
    work_shift = fields.Selection(
        string='Tipo',
        size=1,
        selection=[
            ('M', 'Matutino'),
            ('N', 'Nocturno'),
            ('R', 'Rola turno')
        ]
    )
    work_hours = fields.Float(
        string='Horas por día',
        default=8,
        help='Horas de trabajo por día laborable'
    )


    @api.model
    def create(self, vals):

        rec = super(hr_timecheck_turn, self).create(vals)

        rec.sudo().write({
            'name': self.create_name(rec)
        })

        return rec

    @api.onchange('start_turn', 'start_break',  'end_break', 'end_turn')
    def check_change_time(self):

        self.name = self.create_name()

    def create_name(self, rec = False):

        rec_obj = rec or self

        return 'E: %s%sS: %s' % (
            self.float2time(rec_obj.start_turn),
            ' ER: %s, SR: %s ' % (self.float2time(rec_obj.start_break), self.float2time(rec_obj.end_break)) if rec_obj.has_break else ' ',
            self.float2time(rec_obj.end_turn)
        )

    def float2time(self, _value, time_format = False):
        parts = ('%.2f' % _value).split('.')

        return '%02d:%02d%s' % (int(parts[0]), round(int(parts[1]) * 0.6), ':00' if time_format else '')

    def get_checks(self, base_date):

        res = {}

        if self.has_break:
            checks = {
                '1': 'start_turn',
                '2': 'start_break',
                '3': 'end_break',
                '4': 'end_turn'
            }
        else:
            checks = {
                '1': 'start_turn',
                '2': 'end_turn'
            }

        for check in checks:

            check_index = checks[check]

            if self.hour_mode == '2' and check_index == 'end_turn':
                base_date = (datetime.strptime(base_date, DEFAULT_SERVER_DATE_FORMAT) + timedelta(days=1)).date()

            res[check] = datetime.strptime(
                '%s %s' % (base_date, self.float2time(self[check_index], True)),
                DEFAULT_SERVER_DATETIME_FORMAT
            )

        return res
