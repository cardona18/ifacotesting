# -*- coding: utf-8 -*-

import base64

from openerp import http
from openerp.http import request
from openerp.addons.web.controllers.main import serialize_exception,content_disposition

class HelpUser(http.Controller):

    @http.route('/web/help/user', type='http', auth="user", website=True)
    @serialize_exception
    def help_user(self, **kw):

        manuals = http.request.env['help.user.manual'].sudo().search([])

        return http.request.render('help_custom.help_user_main', {
            'manuals': manuals
        })

    @http.route('/web/help/show/<id>', type='http', auth="user")
    @serialize_exception
    def help_show(self, id, **kw):

        manuals = http.request.env['help.user.manual'].sudo().search([('id','=',id)], limit=1)

        return request.make_response(
            base64.b64decode(manuals[0].manual),
            [
                ('Content-Type', 'application/pdf'),
                ('Content-Disposition: inline;', content_disposition('manual.pdf'))
            ]
        )