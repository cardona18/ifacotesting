# -*- coding: utf-8 -*-
# © <2016> <Juan Carlos Vazquez Beas (jcvazquez@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models

class hr_general_quest_360(models.Model):
    _name = 'hr.general.quest.360'
    _sql_constraints = [
        ('name', 'unique(name)', 'No puedes crear una pregunta con la misma leyenda.')
    ]


    name = fields.Char(
        string="Pregunta",
        required=True
    )
    options_quest  = fields.Selection(
        [
            ('boolean', 'SI o No'),
            ('average', 'Porcentaje'),
            ('cal_num', 'Calificación del 1  al 5')
        ], 
        string="Tipo de respuesta", 
        required=1
    )
    general_type   = fields.Selection(
        [
            ('performance', 'Desempeño'),
            ('potential', 'Potencial'),
        ], 
        string='Tipo',
        required=1,
        index=True
    )