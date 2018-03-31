# -*- coding: utf-8 -*-
# © <2016> <Juan Carlos Vazquez Beas (jcvazquez@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models

class hr_applicant_gi_web(models.Model):
	_inherit        = 'hr.applicant'
	_description    = 'Extensión de la clase hr_applicant para adecuaciones sitio web'
	

	address = fields.Char(
		string='Lugar de residencia',
	)

	internship = fields.Boolean(
		string='Recién egresado',
	)

	env_job= fields.Char(
		string='Ambiente laboral',
	)
	home_job= fields.Char(
		string='Cercanía con mi casa',
	)
	code_job= fields.Char(
		string='Código de vestimenta',
	)
	flexi_job= fields.Char(
		string='Flexibilidad de horarios',
	)
	facilities_job= fields.Char(
		string='Instalaciones',
	)
	feedback_job= fields.Char(
		string='Frecuencia de retroalimentación',
	)
	benefits_job= fields.Char(
		string='Prestaciones y beneficios',
	)
	salary_job= fields.Char(
		string='Salario',
	)
	technology_job= fields.Char(
		string='Tecnología utilizada',
	)
	social_job= fields.Char(
		string='Vida social',
	)