# -*- coding: utf-8 -*-
# © <2017> <Omar Torres Silva (otorresgi18@gmail.com)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime
import logging

from openerp import fields, models
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT

_logger = logging.getLogger(__name__)

class hr_timecheck_sync(models.Model):
    _name = 'hr.timecheck.sync'
    _description = 'HR TIMECHECK SYNC'

    node_id = fields.Many2one(
        string='Nodo',
        comodel_name='hr.timecheck.node'
    )
    name = fields.Char(
        string='Nombre',
        size=80,
        required=True
    )
    code = fields.Char(
        string='Código',
        size=2,
        required=True
    )
    check_time = fields.Datetime(
        string='Sincronización'
    )
    sync_limit = fields.Integer(
        string='Limite',
        help="Tolerancia en segundos para sincronización",
        default=10
    )

    def elapsed_time(self, _datetime = False, to_minutes = False):

        elapsed = 0

        if not self.check_time:
            return elapsed

        current_time = datetime.strptime(_datetime, DEFAULT_SERVER_DATETIME_FORMAT) if _datetime else datetime.now()
        last_time = datetime.strptime(self.check_time, DEFAULT_SERVER_DATETIME_FORMAT)
        sec_diff = (current_time - last_time).total_seconds()

        return int(sec_diff / 60) if to_minutes else int(sec_diff)