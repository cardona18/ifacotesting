# -*- coding: utf-8 -*-
# © <2016> <Omar Torres Silva (otorres@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import locale
import os
import sys
from lxml import etree as ET
from datetime import datetime

from openerp import fields, models
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT

from num2words import Numero_a_Texto

class hr_council_voucher(models.Model):
    _name = 'hr.council.voucher'
    _description = 'HR COUNCIL VOUCHER'

    name = fields.Char(
        string='UUID'
    )
    member_id = fields.Many2one(
        string='Persona',
        comodel_name='hr.council.member'
    )
    payment_date = fields.Date(
        string='Fecha pago'
    )
    xml = fields.Text(
        string='XML'
    )
    folio = fields.Char(
        string='Folio'
    )
    company_id = fields.Many2one(
        string='Empresa',
        comodel_name='res.company'
    )
    lot_id = fields.Many2one(
        string='Lote de recibos',
        comodel_name='hr.council.lot',
        ondelete='cascade'
    )
    last_error = fields.Text(
        string='Error'
    )
    state = fields.Selection(
        string='Estado',
        size=3,
        default='GEN',
        selection=[
            ('GEN', 'Generado'),
            ('ERR', 'Error'),
            ('SIG', 'Timbrado')
        ]
    )

    def parse_xml(self):

        """
        Convert xml file to object
        """

        reload(sys)
        sys.setdefaultencoding('utf-8')

        return ET.fromstring(str(self.xml))

    def num2text(self, num):

        return Numero_a_Texto(num)

    def currency_format(self, _amount, _locale = 'es_MX.UTF-8'):

        # Convenrt date to locale format
        locale.setlocale(locale.LC_ALL, _locale)

        return locale.currency(_amount, grouping=True)

    def current_date(self, _format, _locale = 'es_MX.UTF-8'):

        # SET SYSTEM LOCALE
        locale.setlocale(locale.LC_ALL, _locale)

        return datetime.today().strftime(_format)

