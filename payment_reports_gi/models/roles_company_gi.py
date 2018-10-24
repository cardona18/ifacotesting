# -*- coding: utf-8 -*-
# © <2018> <Mateo Alexander Zabala Gutierrez (mzabalagutierrez@gmail.com)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from odoo import fields, models

_logger = logging.getLogger(__name__)

class res_company_gi(models.Model):
    """
    Hereda el modelo de res company y le agrega 3 campos de el usuario que autoriza, aprueba y otro que elabora, todos cambian dependiendo de la empresa.
    """

    _inherit = 'res.company'

    employee_autorizo = fields.Many2one(
        'hr.employee',
        string='Empleado que autoriza',
    )
    employee_aprobo = fields.Many2one(
        'hr.employee',
        string='Empleado que aprueba',
    )

    employee_elaboro = fields.Many2one(
        'hr.employee',
        string='Empleado que elabora',
    )





