# -*- coding: utf-8 -*-
# © <2016> <Omar Torres Silva (otorres@grupoifaco.com.mx) >
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api

class project_issue_gi(models.Model):
    _inherit = 'project.issue'

    story_id = fields.Many2one(
        string='Historia',
        comodel_name='project.scrum.us'
    )
    state = fields.Selection(
        string='Estado',
        size=1,
        default='O',
        selection=[
            ('O', 'Abierta'),
            ('C', 'Cerrada')
        ]
    )

    @api.multi
    def close_action(self):
        self.state = 'C'

    @api.multi
    def open_action(self):
        self.state = 'O'