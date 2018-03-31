# -*- coding: utf-8 -*-

import logging
import os
import urllib

from openerp import http
from openerp.http import request
from openerp.addons.web.controllers.main import content_disposition

_logger = logging.getLogger(__name__)

class IreportManager(http.Controller):

    @http.route('/web/ireport/download_manager', type='http', auth="user")
    def content_manage(self, **kw):

        file_path = urllib.unquote_plus(kw['path'])

        if kw['type'] == 'html':
            return open(file_path,'r').read()

        return request.make_response(
            open(file_path,'r').read(),
            [
                ('Content-Type', 'application/pdf'),
                ('Content-Disposition: inline;', content_disposition(os.path.basename(file_path)))
            ]
        )