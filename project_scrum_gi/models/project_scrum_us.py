# -*- coding: utf-8 -*-
# © <2017> <Omar Torres Silva (otorresgi18@gmail.com)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api
from odoo.exceptions import UserError

class project_scrum_us(models.Model):
    _name = 'project.scrum.us'
    _description = 'PROJECT SCRUM US'

    name = fields.Char(
        string='Código',
        required=True
    )
    project_id = fields.Many2one(
        string='Proyecto',
        comodel_name='project.project'
    )
    sprint_id = fields.Many2one(
        string='Sprint',
        comodel_name='project.scrum.sprint'
    )
    description = fields.Html(
        string='Descripción'
    )
    issue_ids = fields.One2many(
        string='Incidencias',
        comodel_name='project.issue',
        inverse_name='story_id'
    )
    story_points = fields.Integer(
        string='Puntos de historia',
        default=0
    )
    sequence = fields.Integer(
        string='Prioridad',
        default=0
    )
    state = fields.Selection(
        string='Estado',
        size=6,
        default='open',
        selection=[
            ('open', 'Abierta'),
            ('closed', 'Cerrada')
        ]
    )

    @api.multi
    def close_action(self):

        for issue_id in self.issue_ids:

            if issue_id.state == 'O':
                raise UserError('No es posible cerrar ya que existen incidencias abiertas')

        self.state = 'closed'

    @api.multi
    def open_action(self):
        self.state = 'open'
