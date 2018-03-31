# -*- coding: utf-8 -*-
# © <2017> <Omar Torres Silva (otorresgi18@gmail.com)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime
import logging
import uuid

from openerp import fields, models, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class hr_holidays_request(models.Model):
    _name = 'hr.holidays.request'
    _description = 'HR HOLIDAYS REQUEST'

    name = fields.Char(
        string='Nombre'
    )
    employee_id = fields.Many2one(
        string='Empleado',
        comodel_name='hr.employee',
        default=lambda self: self._current_employee_id()
    )
    company_id = fields.Many2one(
        string='Empresa',
        comodel_name='res.company',
        related='employee_id.company_id'
    )
    worker_request = fields.Boolean(
        string='Otro empleado',
        default=False
    )
    worker_id = fields.Many2one(
        string='Empleado',
        comodel_name='hr.employee'
    )
    worker_company_id = fields.Many2one(
        string='Empresa',
        comodel_name='res.company',
        related='worker_id.company_id'
    )
    check_id = fields.Many2one(
        string='Autoriza',
        comodel_name='res.users'
    )
    check_user = fields.Boolean(
        string='Revisor',
        compute=lambda self: self._compute_check_user()
    )
    from_time = fields.Date(
        string='Desde',
        required=True
    )
    to_time = fields.Date(
        string='Hasta',
        required=True
    )
    access_token = fields.Char(
        string='Token',
        size=50
    )
    state = fields.Selection(
        string='Estado',
        default='NEW',
        size=4,
        selection=[
            ('NEW', 'Creada'),
            ('SEND', 'Enviada'),
            ('OK', 'Autorizada'),
            ('REJ', 'Rechazada'),
        ]
    )

    @api.model
    def create(self, vals):

        if 'from_time' not in vals.keys() or 'to_time' not in vals.keys():
            raise UserError('No es posible crear la solicitud')

        rec = super(hr_holidays_request, self).create(vals)

        rec.sudo().write({
            'name': 'HR-%s' % str(rec.id).zfill(6)
        })

        return rec

    def _current_employee_id(self):

        employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

        if not employee.id:
            raise UserError('No es posible crear solicitudes, contacte al departamento de Soporte técnico')

        if not employee.parent_id and not employee.coach_id:
            raise UserError('No es posible crear solicitudes, contacte al departamento de RH - Nómina')

        return employee.id

    def _compute_check_user(self):

        for item in self:
            item.check_user = self.env.uid == self.check_id.id and self.state == 'SEND'

    @api.multi
    def action_send(self):

        check_employee = self.employee_id.parent_id or self.employee_id.coach_id

        if not check_employee:
            raise UserError('No es posible enviar la solicitud, contacte al departamento de RH - Nómina')

        if not check_employee.user_id:
            raise UserError('La persona que autoriza sus solicitudes no cuenta con un usuario asociado al empleado, contacte al departamento de RH - Nómina')

        self.check_id = check_employee.user_id.id
        self.state = 'SEND'
        self.access_token = str(uuid.uuid4()).replace('-','')

        template = self.env['mail.template'].sudo().search([('name', '=', 'PENDING_APPROVE_HOLIDAYS_NOTIFY_TEMPLATE')], limit=1)
        template.send_mail(self.id, force_send=True)

    @api.multi
    def action_approve(self):
        self.action_check('OK')

    @api.multi
    def action_direct_approve(self):
        self.action_check('OK')
        self.sudo().sync_state = 'SYNC'

    @api.multi
    def action_decline(self):
        self.action_check('REJ')

    def action_check(self, _state):

        self.sudo().state = _state

        template = self.env['mail.template'].sudo().search([('name', '=', 'HOLIDAYS_REQUEST_RESULT_NOTIFY_TEMPLATE')], limit=1)
        template.send_mail(self.id, force_send=True)