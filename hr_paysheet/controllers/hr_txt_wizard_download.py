# -*- coding: utf-8 -*-

from openerp import http
from openerp.http import request
from openerp.addons.web.controllers.main import serialize_exception,content_disposition

class XMlPrinter(http.Controller):

    @http.route('/web/wizard/txt_download/', type='http', auth="user")
    @serialize_exception
    def sua_file_download(self, id, model, filename, **kw):
        """ Download txt file from wizard.
        @returns: :class:`werkzeug.wrappers.Response`
        """

        wizard = http.request.env[model].search([('id','=',id)], limit=1)

        return request.make_response(
            wizard.txt_content,
            [
                ('Content-Type', 'text/plain'),
                ('Content-Disposition', content_disposition(filename))
            ]
        )

    @http.route('/web/download/raw_file/', type='http', auth="user")
    @serialize_exception
    def raw_file_download(self, path, _type, filename, **kw):
        """ Download raw file.
        @returns: :class:`werkzeug.wrappers.Response`
        """

        return request.make_response(
            open(path, "rb").read(),
            [
                ('Content-Type', _type),
                ('Content-Disposition', content_disposition(filename))
            ]
        )