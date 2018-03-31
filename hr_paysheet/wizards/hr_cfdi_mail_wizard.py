# -*- coding: utf-8 -*-
# © <2017> <Omar Torres (otorresgi18@gmail.com)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from random import randint
import logging

from odoo import fields, models, api
from odoo.exceptions import Warning

_logger = logging.getLogger(__name__)

class hr_cfdi_mail_wizard(models.TransientModel):
    _name = 'hr.cfdi.mail.wizard'
    _description = 'HR CFDI MAIL WIZARD'


    mail_action = fields.Selection(
        string='Acción',
        default='CHECK_TOKEN',
        selection=[
            ('CHECK_TOKEN', 'Validar token'),
            ('SEND_TOKEN', 'Enviar token')
        ]
    )
    employee_id = fields.Many2one(
        string='Empleado',
        comodel_name='hr.employee'
    )
    cfdi_token = fields.Char(
        string='Token'
    )

    @api.multi
    def cfdi_mail_action(self):

        if self.mail_action == 'SEND_TOKEN':

            self.employee_id.cfdi_mail_token = randint(1000, 9999)
            self.employee_id.cfdi_mail_ok = False

            template = self.env.ref('hr_paysheet.cfdi_mail_send_token_template')

            self.env['mail.template'].browse(template.id).sudo().send_mail(self.employee_id.id, force_send=True)

        if self.mail_action == 'CHECK_TOKEN':

            if str(self.employee_id.cfdi_mail_token) == str(self.cfdi_token):
                self.employee_id.cfdi_mail_ok = True
            else:
                raise Warning('El token no coincide.')