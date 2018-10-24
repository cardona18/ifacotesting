# -*- coding: utf-8 -*-

from datetime import datetime
from random import randint
import logging
import os

from openerp import http
from openerp.addons.web.controllers.main import serialize_exception,content_disposition
from openerp.http import request

_logger = logging.getLogger(__name__)

class TimecheckMonitor(http.Controller):

    @http.route('/web/project_scrum/monitor', type='http', auth="user")
    @serialize_exception
    def project_scrum_monitor(self, **kw):
        """ @returns: :class:`werkzeug.wrappers.Response` """

        sprint = http.request.env['project.scrum.sprint'].search([('state','=', 'open'), ('project_id', '=', int(kw['pid']))], limit=1)

        if not sprint.id:
            return ''

        return http.request.render('project_scrum_gi.project_scrum_board_template', {
            'project_id': int(kw['pid']),
            'task_type_id': int(kw['tid']),
            'sprint': sprint
        })

    @http.route('/web/project_scrum/monitor_data', type='http', auth="user", csrf=False)
    @serialize_exception
    def project_scrum_monitor_data(self, **kw):
        """ @returns: :class:`werkzeug.wrappers.Response` """

        sprint = http.request.env['project.scrum.sprint'].search([('state','=', 'open'), ('project_id', '=', int(kw['project_id']))], limit=1)
        all_us = http.request.env['project.scrum.us'].search([('project_id', '=', int(kw['project_id']))])

        sp_done = 0
        sp_pending = 0
        pro_done = 0
        pro_pending = 0
        label_done = "SP COMPLETOS: %s"
        label_pending = "SP PENDIENTES: %s"
        colors = [
            'rgb(255, 99, 132)',
            'rgb(255, 159, 64)',
            'rgb(255, 205, 86)',
            'rgb(75, 192, 192)',
            'rgb(54, 162, 235)',
            'rgb(153, 102, 255)',
            'rgb(201, 203, 207)'
        ]
        chart_data = """{
            "data": [%s,%s],
            "background": ["%s", "%s"],
            "labels": ["%s","%s"],
            "pdata": [%s,%s],
            "pbackground": ["%s", "%s"],
            "plabels": ["%s","%s"],
            "title": "%s"
        }"""

        if not sprint.id:
            return chart_data % (
                sp_done,
                sp_pending,
                colors[randint(0, 2)],
                colors[randint(3, 6)],
                label_done % sp_done,
                label_pending % sp_pending,
                pro_done,
                pro_pending,
                colors[randint(0, 2)],
                colors[randint(3, 6)],
                label_done % pro_done,
                label_pending % pro_pending,
                ' '
            )

        for us in sprint.story_ids:
            sp_done += us.story_points if us.state == 'closed' else 0
            sp_pending += us.story_points if us.state == 'open' else 0

        for us in all_us:
            pro_done += us.story_points if us.state == 'closed' else 0
            pro_pending += us.story_points if us.state == 'open' else 0

        return chart_data % (
            sp_done,
            sp_pending,
            colors[randint(0, 2)],
            colors[randint(3, 6)],
            label_done % sp_done,
            label_pending % sp_pending,
            pro_done,
            pro_pending,
            colors[randint(0, 2)],
            colors[randint(3, 6)],
            label_done % pro_done,
            label_pending % pro_pending,
            '%s - %s' % (sprint.name,  sprint.goal)
        )

    @http.route('/web/project_scrum/monitor_tasks', type='http', auth="user", csrf=False)
    @serialize_exception
    def project_scrum_monitor_tasks(self, **kw):
        """ @returns: :class:`werkzeug.wrappers.Response` """

        tasks = http.request.env['project.task'].search([
            ('project_id','=', int(kw['project_id'])),
            ('stage_id', '=', int(kw['stage_id']))
        ])

        return http.request.render('project_scrum_gi.project_scrum_tasks_template', {
            'tasks': tasks
        })