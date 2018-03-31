# -*- coding: utf-8 -*-
# © <2016> <Juan Carlos Vazquez Beas (jcvazquez@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models

class hr_department_gi(models.Model):
	_inherit = 'hr.department'

	type_department = fields.Selection(
	[
		('unity_cate', 'Unidad'),
		('department_categ', 'Departamento'),
		('area_categ', 'Área'),
	], 
	string='Tipo',	
	required=True
	)
	old_id = fields.Integer(
        string='ID odoo 8',
    )
