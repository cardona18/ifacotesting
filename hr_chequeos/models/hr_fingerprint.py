# -*- coding: utf-8 -*-
# © <2017> <Omar Torres Silva (otorresgi18@gmail.com)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api

class hr_fingerprint(models.Model):
    _name = 'hr.fingerprint'
    _description = 'HR FINGERPRINT'

    name = fields.Selection(
        string='Dedo',
        size=2,
        index=True,
        selection=[
            ('L1', 'Meñique izquierdo'),
            ('L2', 'Anular izquierdo'),
            ('L3', 'Medio izquierdo'),
            ('L4', 'Índice izquierdo'),
            ('L5', 'Pulgar izquierdo'),
            ('R1', 'Meñique derecho'),
            ('R2', 'Anular derecho'),
            ('R3', 'Medio derecho'),
            ('R4', 'Índice derecho'),
            ('R5', 'Pulgar derecho'),
        ]
    )
    employee_id = fields.Many2one(
        string='Empleado',
        comodel_name='hr.employee',
        ondelete='cascade'
    )
    hash_value = fields.Text(
        string='Biometría'
    )
    is_check = fields.Boolean(
        string='Ronda',
        default=False
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

    @api.model
    def create(self, vals):

        rec = super(hr_fingerprint, self).create(vals)

        if rec.name:
            rec.sudo().search([
                ('employee_id', '=', rec.employee_id.id),
                ('name', '=', rec.name),
                ('id', '!=', rec.id),
            ]).sudo().unlink()

        return rec