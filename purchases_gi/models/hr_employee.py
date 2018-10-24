# -*- coding: utf-8 -*-
# © <2016> <Juan Carlos Vazquez Beas (jcvazquez@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import sys, logging
from odoo import fields, models, api

_logger = logging.getLogger(__name__)

class hr_employee(models.Model):
    """
    Se heredó la clase para adecuar el flujo de quien aprueba y quien autoriza cuando no se tiene configurados los departamentos.
    """
    _inherit = 'hr.employee'

    purchase_especial = fields.Boolean(
        string='Puede aprobar y autorizar',
    )
    empl_authorize = fields.Many2one(
        'hr.employee',
        string='Empleado que autoriza',
    )
    empl_approve = fields.Many2one(
        'hr.employee',
        string='Empleado que aprueba',
    )

    @api.onchange('user_id')
    def _onchange_user(self):
        """
        Agrega el correo asociado del usuario al empleado.
        """
        self.work_email = self.user_id.email
            

