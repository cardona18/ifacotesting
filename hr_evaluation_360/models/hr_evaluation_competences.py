# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.osv import osv


class hr_eval_comp(models.Model):
	_name = 'hr.eval.comp'

	_sql_constraints = [
		('name', 'unique(name)', 'No puedes crear una competencia con el mismo nombre.')
	]

	name 		  	= fields.Char(
		string='Nombre de la competencia',
		required=True
	)

	definition		= fields.Text(
	    string='Definición',
	    required=True,
	)

	dimension		= fields.Text(
	    string='Dimensión',
	    required=True,
	)
	
	question_ids  = fields.Many2many(
	    'hr.questions.gi',
	    string='Preguntas asociadas',
	    ondelete='cascade'
	)

	@api.multi
	def unlink(self):
		for self_id in self:
			job_com = self.env['hr.job'].search([('competences','=',self_id.name)])
			print(job_com)
			if job_com:
				raise osv.except_osv('Advertencia','No puedes eliminar esta competencia por hay puestos asociados a esta.')
			else:
				return models.Model.unlink(self)
