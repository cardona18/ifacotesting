# -*- coding: utf-8 -*-
# © <2016> <Juan Carlos Vazquez Beas (jcvazquez@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models

class hr_department_gi(models.Model):
	_inherit            = 'hr.department'

	@api.multi
	def get_unit_name_formated(self):
		unit_name_form = self.name.replace('Dirección', 'Unidad')
		return unit_name_form