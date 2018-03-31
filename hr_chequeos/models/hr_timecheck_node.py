# -*- coding: utf-8 -*-
# © <2017> <Omar Torres Silva (otorresgi18@gmail.com)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime
import logging

from openerp import fields, models, api
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT

_logger = logging.getLogger(__name__)

class hr_timecheck_node(models.Model):
    _name = 'hr.timecheck.node'
    _description = 'HR TIMECHECK NODE'

    _sql_constraints = [
        ('unique_node_num', 'unique(node_num)', 'El número de nodo ya se encuentra asignado.')
    ]

    name = fields.Char(
        string='Nombre',
        required=True,
        size=80
    )
    node_num = fields.Integer(
        string='Número',
        default=1
    )
    ip_addr = fields.Char(
        string='IP',
        size=20
    )
    hw_addr = fields.Char(
        string='ID Hardware',
        size=60
    )
    sync_count = fields.Char(
        string='Registros',
        size=60
    )
    sync_count2 = fields.Char(
        string='Registros',
        size=60
    )
    last_node_time = fields.Datetime(
        string='Fecha y hora nodo'
    )
    last_error = fields.Text(
        string='Último error'
    )
    time_ids = fields.One2many(
        string='Sincronización',
        comodel_name='hr.timecheck.sync',
        inverse_name='node_id'
    )
    time_diff = fields.Integer(
        string='Delay',
        compute=lambda self: self._compute_time_diff()
    )
    sync_state = fields.Selection(
        string='Sincronización',
        default='OK',
        size=4,
        index=True,
        selection=[
            ('SYNC', 'Sincronizar'),
            ('OK', 'Sincronizado')
        ]
    )

    def _compute_time_diff(self):

        for item in self:
            item.time_diff = 0

    def status_class(self):

        if not self.ip_addr:
            return ['off_state', 'OFFLINE']

        for time_id in self.time_ids:

            if time_id.elapsed_time() > time_id.sync_limit:
                return ['error_state', time_id.name]

        return ['ok_state', 'OK']

    @api.multi
    def parse_alive(self, values):

        node = self.browse(values['node_id'])
        time_id = self.time_ids.search([('node_id', '=', node.id), ('code', '=', values['type'])], limit=1) if node.id else False

        if time_id.id:
            time_id.check_time = datetime.now()
            return True

        if node.id and values['type'] == 'CONN':
            node_time = datetime.strptime(values['node_time'], DEFAULT_SERVER_DATETIME_FORMAT)
            node.last_node_time = node_time
            node.ip_addr = values['ip_addr']
            node.sync_count = values['count_str']
            node.sync_count2 = values['count_str2']
            return True

        return False

    def sync_txt(self):

        res = ''

        if not self.ip_addr:
            return ''

        for time_id in self.time_ids:
            res += '%s: %s ' % (time_id.code, time_id.elapsed_time())

        return res.strip()

    @api.onchange('ip_addr')
    def _check_ip(self):

        if not self.ip_addr:
            self.reset_values()


    def reset_values(self):
        self.ip_addr = False
        self.sync_count = False
        self.sync_count2 = False
        self.last_node_time = False

    @api.multi
    def reset_node(self):
        self.reset_values()

    def get_ip_str(self):
        return '%s - %s' % (self.ip_addr, self.time_diff) if self.ip_addr else ''