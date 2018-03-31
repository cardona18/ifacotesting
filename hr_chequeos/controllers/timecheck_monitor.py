# -*- coding: utf-8 -*-

from datetime import datetime
import logging
import os

from openerp import http
from openerp.addons.web.controllers.main import serialize_exception,content_disposition
from openerp.http import request

_logger = logging.getLogger(__name__)

class TimecheckMonitor(http.Controller):

    @http.route('/web/timechecker/monitor', type='http', auth="user")
    @serialize_exception
    def timecheck_monitor_main(self, **kw):
        """ Time checker monitor.
        @returns: :class:`werkzeug.wrappers.Response`
        """

        nodes = http.request.env['hr.timecheck.node'].search([])
        agent = http.request.httprequest.environ.get('HTTP_USER_AGENT', '')
        browser = 'default'

        if agent.find('MSIE') > 0:
            browser = 'ie'

        if agent.find('Trident') > 0:
            browser = 'ie'

        if agent.find('Firefox') > 0:
            browser = 'firefox'

        if agent.find('Chrome') > 0:
            browser = 'chrome'

        return http.request.render('hr_chequeos.timecheck_monitor', {
            'nodes': nodes,
            'browser': browser
        })

    @http.route('/web/timechecker/content', type='http', auth="user", csrf=False)
    @serialize_exception
    def timecheck_monitor_contents(self, **kw):
        """ Time checker monitor content.
        @returns: :class:`werkzeug.wrappers.Response`
        """

        nodes = http.request.env['hr.timecheck.node'].search([])

        return http.request.render('hr_chequeos.timecheck_monitor_content', {
            'nodes': nodes
        })

    @http.route('/web/timechecker/current_date', type='http', auth="user", csrf=False)
    @serialize_exception
    def timecheck_monitor_current_date(self, **kw):
        """ Time checker monitor current_date.
        @returns: :class:`werkzeug.wrappers.Response`
        """

        # SET SYSTEM TIMEZONE
        os.environ['TZ'] = "America/Mexico_City"

        return datetime.now().isoformat()[:19].replace('T',' ')