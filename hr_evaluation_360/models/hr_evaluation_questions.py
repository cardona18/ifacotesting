# -*- coding: utf-8 -*-

from openerp import models, fields, api

class hr_questions_gi(models.Model):
	_name 			= 'hr.questions.gi'

	_sql_constraints = [
		('name', 'unique(name)', 'No puedes crear una pregunta con la misma leyenda.')
	]


	name 			= 	fields.Char(
							string="Pregunta",
							required=True
						)

	options_quest  	= fields.Selection([('boolean', 'SI o No'),
										('average', 'Porcentaje'),
										('cal_num', 'Calificación del 1  al 5')], string="Tipo de respuesta", required=1)

