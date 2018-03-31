# -*- coding: utf-8 -*-
# © <2016> <Juan Carlos VB (jcvazquez@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models

class average_compe(models.Model):
    _name = 'average.compe'

    comp_id = fields.Many2one(
		string='Competencia',
		comodel_name='hr.eval.comp'
	)

    average_comp = fields.Float(
        'Promedio',
    )

    comp_average_ids = fields.Many2one(
		string='Competencias y promedios',
		comodel_name='hr.evaluation.360'
	)
