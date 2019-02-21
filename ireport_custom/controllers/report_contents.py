# -*- coding: utf-8 -*-

import logging
import os
from urllib.parse import unquote_plus

from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.main import content_disposition

_logger = logging.getLogger(__name__)

class IreportManager(http.Controller):

    @http.route('/web/ireport/download_manager', type='http', auth="user")
    def content_manage(self, **kw):

        file_path = unquote_plus(kw['path'])

        if kw['type'] == 'html':
            return open(file_path, 'rb').read()

        return request.make_response(
            open(file_path, 'rb').read(),
            [
                ('Content-Type', 'application/pdf'),
                ('Content-Disposition: inline;', content_disposition(os.path.basename(file_path)))
            ]
        )