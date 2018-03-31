# -*- coding: utf-8 -*-

from openerp import http
from openerp.http import request
from openerp.addons.web.controllers.main import serialize_exception,content_disposition
import base64
class XMlPrinter(http.Controller):

    @http.route('/web/binary/download_document', type='http', auth="user")
    @serialize_exception
    def download_document(self,id, **kw):
        """ Download cfdi xml file.
        @param str id: id of the record from which to fetch the xml
        @returns: :class:`werkzeug.wrappers.Response`
        """

        CFDI = http.request.env['hr.xml.cfdi'].search([('id','=',id)], limit=1)

        if(not CFDI.id):
            return request.not_found()

        filename = 'cfdi_%s.xml' % (id)

        return request.make_response(
            CFDI.xml_string,
            [
                ('Content-Type', 'text/xml'),
                ('Content-Disposition', content_disposition(filename))
            ]
        )