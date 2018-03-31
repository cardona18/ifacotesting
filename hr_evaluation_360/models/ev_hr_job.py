# -*- coding: utf-8 -*-
# © <2016> <Juan Carlos Vazquez Beas (jcvazquez@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models

class ev_hr_job(models.Model):
	_inherit 		= 'hr.job'

	competences  	= fields.Many2many(
		'hr.eval.comp',
		string='Competencias del puesto',
		ondelete='cascade'
	)

