# -*- coding: utf-8 -*-
# © <2016> <Omar Torres Silva (otorres@grupoifaco.com.mx) >
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api

class project_task_gi(models.Model):
    _inherit = 'project.task'

    sprint_id = fields.Many2one(
        string='Sprint',
        comodel_name='project.scrum.sprint'
    )
    story_id = fields.Many2one(
        string='Historia',
        comodel_name='project.scrum.us'
    )
    task_type = fields.Selection(
        string='Tipo',
        size=1,
        default='P',
        selection=[
            ('P', "Planeada"),
            ('N', "No Planeada")
        ]
    )
    story_points = fields.Float(
        string='Puntos de historia',
        digits=(16, 2)
    )
    work_state = fields.Selection(
        string='Estado',
        default='stop',
        size=7,
        selection=[
            ('running', 'En proceso'),
            ('paused', 'Pausa'),
            ('stop', 'Detenida')
        ]
    )