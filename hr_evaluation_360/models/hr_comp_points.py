# -*- coding: utf-8 -*-
# © <2016> <Juan Carlos Vazquez Beas (jcvazquez@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api

class hr_comp_points(models.Model):
	_name = 'hr.comp.points'
	_description = 'HR COMP POINTS'

	comp_id = fields.Many2one(
		string='Competencia',
		comodel_name='hr.eval.comp'
	)

	point_comp = fields.Integer(
		'Ponderación',
		size=3,
		required=True,
	)

	question_ids  = fields.Many2many(
		'hr.questions.gi',
		string='Preguntas a evaluar',
		ondelete='cascade'
	)

	comp_points = fields.Many2one(
		string='plan',
		comodel_name='hr.plan.evaluation'
	)



	@api.onchange('comp_id')
	def onchange_evaluated_get_quest(self):
		for quest_ids in self.comp_id.question_ids:
			print(quest_ids)



	@api.onchange('point_comp')
	def onchange_evaluated_get_comp(self):
		if self.point_comp > 100:
			self.point_comp = 0
			return {'value':{},'warning':{'title':'Advertencia','message':'No puedes asignar una cantidad mayor a 100'}}
