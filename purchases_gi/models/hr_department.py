# -*- coding: utf-8 -*-
# © <2017> <Juan Carlos Vazquez Beas (jcvazquez@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api

class hr_department_gi(models.Model):
	"""
    Se heredó la clase para adecuar la funcionalidad requerida y se agregaron campos
    """
	_inherit = 'hr.department'

	hr_busi_segme = fields.Many2one(
		'account.analytic.account',
		string='Segmentos analíticos',
	)
	project_development = fields.Boolean(
		string='Proyecto o desarrollo',
	)
	employee_assigned = fields.Many2one(
		'hr.employee',
		string='Personal de compras asignado',
		track_visibility="onchenge", required=True
	)
