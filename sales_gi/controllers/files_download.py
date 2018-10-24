# -*- coding: utf-8 -*-

import os
from urllib.parse import unquote_plus

from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.main import serialize_exception,content_disposition

class FilesDownload(http.Controller):

    @http.route('/web/files/download', type='http', auth="user")
    @serialize_exception
    def file_download(self, path, **kw):
        """ Download file by path.
        @returns: :class:`werkzeug.wrappers.Response`
        """

        zip_file = open(unquote_plus(path), 'rb')

        return request.make_response(
            zip_file.read(),
            [
                ('Content-Type', 'application/zip'),
                ('Content-Disposition', content_disposition(os.path.basename(zip_file.name)))
            ]
        )