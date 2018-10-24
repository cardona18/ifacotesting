# -*- coding: utf-8 -*-
# © <2016> <Juan Carlos Vazquez Beas (jcvazquez@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api

class hr_employee(models.Model):
    _inherit = 'hr.employee'

    is_analysis = fields.Boolean(
        string='Analista',
    )