# -*- coding: utf-8 -*-
# © <2017> <Omar Torres Silva (otorresgi18@gmail.com)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api

class project_scrum_monitor_wizard(models.TransientModel):
    _name = 'project.scrum.monitor.wizard'
    _description = 'PROJECT SCRUM MONITOR WIZARD'

    project_id = fields.Many2one(
        string='Proyecto',
        comodel_name='project.project'
    )
    task_type_id = fields.Many2one(
        string='Etapa',
        comodel_name='project.task.type'
    )

    @api.multi
    def show_monitor(self):

        return {
            'type' : 'ir.actions.act_url',
            'url': '/web/project_scrum/monitor?pid=%s&tid=%s' % (self.project_id.id, self.task_type_id.id),
            'target': 'new'
        }