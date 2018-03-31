# -*- coding: utf-8 -*-

import os
import urllib

from openerp import http
from openerp.http import request
from openerp.addons.web.controllers.main import serialize_exception,content_disposition

class ZIPDownload(http.Controller):

    @http.route('/web/binary/zip_file_download', type='http', auth="user")
    @serialize_exception
    def sua_file_download(self, path, **kw):
        """ Download zip file.
        @returns: :class:`werkzeug.wrappers.Response`
        """

        zip_file = open(urllib.unquote(path), 'r')

        return request.make_response(
            zip_file.read(),
            [
                ('Content-Type', 'application/zip'),
                ('Content-Disposition', content_disposition(os.path.basename(zip_file.name)))
            ]
        )