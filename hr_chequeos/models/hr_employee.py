# -*- coding: utf-8 -*-
# © <2016> <Omar Torres Silva (otorres@grupoifaco.com.mx) >
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api

class hr_employee_gi(models.Model):
    _inherit = 'hr.employee'

    turn_id = fields.Many2one(
        string='Turno',
        comodel_name='hr.timecheck.turn'
    )
    check_node_id = fields.Many2one(
        string='Nodo',
        comodel_name='hr.timecheck.node'
    )
    has_delays = fields.Boolean(
        string='No considerar retardos'
    )
    fingerprint_ids = fields.One2many(
        string='Biometrías',
        comodel_name='hr.fingerprint',
        inverse_name='employee_id'
    )
    add_saturday = fields.Boolean(
        string='Incluir sabado',
        default=True
    )
    sync_state = fields.Selection(
        string='Sincronización',
        default='SYNC',
        size=4,
        index=True,
        selection=[
            ('SYNC', 'Sincronizar'),
            ('OK', 'Sincronizado')
        ]
    )

    @api.onchange('check_node_id','turn_id','image')
    def check_check_node_id(self):
        self.sync_state = 'SYNC'

        for fp in self.fingerprint_ids:
            fp.sync_state = 'SYNC'