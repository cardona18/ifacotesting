# -*- coding: utf-8 -*-
# © <2017> <Omar Torres Silva (otorresgi18@gmail.com)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api

class project_scrum_sprint(models.Model):
    _name = 'project.scrum.sprint'
    _description = 'PROJECT SCRUM SPRINT'

    name = fields.Char(
        string='Sprint',
        required=True
    )
    project_id = fields.Many2one(
        string='Proyecto',
        comodel_name='project.project'
    )
    from_date = fields.Date(
        string='Inicio',
        required=True
    )
    to_date = fields.Date(
        string='Cierre',
        required=True
    )
    goal = fields.Char(
        string='Meta',
        size=120
    )
    story_points = fields.Integer(
        string='Puntos de historia',
        default=0
    )
    story_ids = fields.One2many(
        string='Historias de usuario',
        comodel_name='project.scrum.us',
        inverse_name='sprint_id'
    )
    stories_count = fields.Integer(
        string='Historias de usuario',
        default=0,
        compute=lambda self: self._compute_stories_count()
    )
    task_ids = fields.One2many(
        string='Backlog',
        comodel_name='project.task',
        inverse_name='sprint_id'
    )
    task_count = fields.Integer(
        string='Backlog',
        default=0,
        compute=lambda self: self._compute_task_count()
    )
    state = fields.Selection(
        string='Estado',
        size=6,
        default='open',
        selection=[
            ('open', 'Abierto'),
            ('closed', 'Cerrado')
        ]
    )

    def _compute_stories_count(self):
        self.stories_count = self.story_ids.search_count([('sprint_id', '=', self.id)])

    def _compute_task_count(self):
        self.task_count = self.task_ids.search_count([('sprint_id', '=', self.id)])

    @api.multi
    def close_action(self):
        self.state = 'closed'

    @api.multi
    def open_action(self):
        self.state = 'open'
