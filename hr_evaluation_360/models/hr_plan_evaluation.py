# -*- coding: utf-8 -*-
# © <2016> <Juan Carlos Vazquez Beas (jcvazquez@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

# 1 : imports of python lib
import locale
import logging
import sys  
# 2 :  imports of openerp
from openerp import models, fields, api
from openerp import SUPERUSER_ID
from openerp import tools
from openerp.osv import osv




class hr_plan_evaluation(models.Model):
	_name 			= 'hr.plan.evaluation'
	_description 	= 'HR plan EVALUATION'

	name = fields.Char(
		string='Nombre del plan',
		required=True,
	)

	evaluated  		= fields.Many2one(
		'hr.job',
		string='Puesto a evaluar',
		required=True,
		ondelete='cascade'
	)

	job_boss = fields.Many2one(
		related='evaluated.job_id_boss',
		string='Jefe evaluador',
		ondelete='cascade',
		readonly=True, 
	)

	department_id  	= fields.Many2one(
		related='evaluated.department_id',
		string='Departamento',
		required=True,
		ondelete='cascade',
		readonly=True
	)

	competences  	= fields.Many2many(
		related='evaluated.competences',
		string='Competencias del puesto',
		required=True,
		readonly=True, 
		ondelete='cascade',
	)

	config_ids = fields.One2many(
		string='Configuración',
		comodel_name='hr.comp.points',
		inverse_name='comp_points',
		ondelete='cascade'
	)

	state = fields.Selection(
		[('create', 'Creado'),
		('executed', 'Plan ejecutado'),
		], string='Estado',
		 default='create'
	)

	start_eval = fields.Date(
		string='Inicio',
		required=True,
	)
	end_eval = fields.Date(
		string='Fin',
		required=True,
	)



	@api.onchange('evaluated')
	def onchange_evaluated_get_comp(self):

		# self.boss_eval = self.evaluated.job_id_boss
		print(self.evaluated.job_id_boss)
		
		conf_ids = []
		ques_ids = []
		
		for competence in self.evaluated.competences:

			for competence_ids in competence:
				for q_ids in competence_ids.question_ids:
					ques_ids.append(q_ids.id)

			print(ques_ids)

			conf_ids.append((0, 0, { 'comp_id': competence.id, 'question_ids' : ques_ids}))

			ques_ids = []


		self.config_ids = conf_ids

		no_id = self.env['hr.comp.points'].search([('comp_points', '=', None)])
		no_id.unlink()



	@api.multi
	def write(self, vals):

		acom = 0
		# print(vals['config_ids'][2])
		try:
			for comp_id in vals['config_ids']:
				# print(comp_id[2])
				if comp_id[2]:
					if comp_id[2]['point_comp']:
						acom += comp_id[2]['point_comp']
				else:
					points = self.env['hr.comp.points'].search([('id', '=', comp_id[1])])
					acom += points.point_comp
			# print("Hoalaa")
			print(acom)
			if acom != 100:
				# print(acom)
				raise osv.except_osv('Advertencia','La ponderación de las competencias debe ser igual a 100.')
			else:
				return super(hr_plan_evaluation, self).write(vals)
				
		except KeyError:
			return super(hr_plan_evaluation, self).write(vals)

	# @api.model
	# def create(self, vals):
	# 	acom = 0
	# 	if vals['config_ids']:
	# 		for comp_id in vals['config_ids']:
	# 			# print(len(comp_id[2]))
	# 			if len(comp_id[2]) != 3:
	# 				raise osv.except_osv('Advertencia','La ponderación de las competencias debe ser igual a 100.')
	# 			if comp_id[2]['point_comp']:
	# 				acom += comp_id[2]['point_comp']
	# 	if acom != 100:
	# 		# print(acom)
	# 		raise osv.except_osv('Advertencia','La ponderación de las competencias debe ser igual a 100.')

	# 	return super(hr_plan_evaluation, self).create(vals)

	@api.multi
	def copy(self, default=None):
		for self_id in self:
			if self_id.config_ids:
				raise osv.except_osv('Advertencia','Por razones de seguridad no puedes duplicar un plan con competencias ya asignadas.')
