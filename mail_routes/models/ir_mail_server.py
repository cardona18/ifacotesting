# -*- coding: utf-8 -*-
# © <2016> <Omar Torres Silva (otorres@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import re
import rfc822
import sys

from openerp import fields, models, api

import logging

_logger = logging.getLogger(__name__)

class ir_mail_server_gi(models.Model):
    _inherit = 'ir.mail_server'

    @api.model
    def send_email(self, message, mail_server_id=None, smtp_server=None, smtp_port=None,
                   smtp_user=None, smtp_password=None, smtp_encryption=None, smtp_debug=False):

        # SEARCH OUT ROUTE
        server_id = self.find_route(message['To'])
        mail_server_id = server_id if server_id else mail_server_id

        result = super(ir_mail_server_gi, self).send_email(
            message, mail_server_id, smtp_server, smtp_port, smtp_user,
            smtp_password, smtp_encryption, smtp_debug
        )

        return result

    def find_route(self, _destination):

        address = rfc822.parseaddr(_destination)

        reload(sys)
        sys.setdefaultencoding('utf-8')

        domain = address[1].split('@')[1]

        for route in self.env['mail.domain.route'].sudo().search([]):

            try:
                exp = re.compile(route.domain_regex)
            except Exception as e:
                _logger.debug("INVALID ROUTE: %s => %s", route.domain_regex, domain)
                return False

            if exp.match(domain):
                _logger.debug("MATCH SMTP OUT RULE: %s => %s", route.domain_regex, domain)
                return route.server_id.id

        return False