# -*- coding: utf-8 -*-
# © <2016> <Juan Carlos Vazquez Beas (jcvazquez@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models

class admin_answers(models.Model):
	_name = 'admin.answers'
	_description = 'Respuestas'

	quest       = fields.Many2one(
		'hr.questions.gi',
		string='Pregunta competencia',
	)

	quest_gen = fields.Many2one(
		'hr.general.quest.360',
		string='Pregunta general',
	)

	comp        = fields.Many2one(
		'hr.eval.comp',
		string='Competencia evaluada',
	)

	evalu_plan  = fields.Many2one(
		'hr.evaluation.360',
		string='Plan ejecutado',
		required=True,
	)

	id_excute_plan = fields.Integer(
		string='Numero de ejecución del plan',
		related='evalu_plan.id_excute_plan',
		ondelete="cascade"
	)

	empl_evalu  = fields.Many2one(
		related='evalu_plan.name_evaluated',
		string='Empleado evaluado',
		required=True,
	)

	type_evaluators   = fields.Selection([('auto_eval', 'Autoevaluación'),
						  ('boss_eval', 'Jefe'),
						  ('partner_eval', 'Compañero'),
						  ('collabo_eval', 'Subordinado'),
						  ('client_eval', 'Cliente'),
						  ], 
		string='Tipo de evaluador',
		required=True
	)

	employee_evaluator  = fields.Many2one(
		'hr.employee',
		string='Empleado evaluador',
		required=True,
	)

	name        = fields.Char(
		string='Respuesta',
		required=True,
	)

	is_general = fields.Boolean(
		string="Es pregunta general"
	)

	general_type   = fields.Selection([
		('performance', 'Desempeño'),
		('potential', 'Potencial'),], 
		string='Tipo de pregunta general',
	)
