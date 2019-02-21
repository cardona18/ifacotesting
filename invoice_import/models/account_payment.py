# -*- coding: utf-8 -*-
# © <2018> < ()>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging

import base64
from datetime import datetime
from itertools import groupby

from lxml import etree
from lxml.objectify import fromstring
from suds.client import Client
from odoo import _, api, fields, models
from odoo.tools import DEFAULT_SERVER_TIME_FORMAT
from odoo.tools.misc import html_escape
from odoo.exceptions import UserError

from . import account_invoice

_logger = logging.getLogger(__name__)


class account_payment(models.Model):
    _inherit = 'account.payment'


    payment_date = fields.Date(
        string='Fecha de pago',
    )
    real_copper = fields.Date(
        string='Fecha de pago',
    )


    # @api.multi
    # def l10n_mx_edi_payment_data(self):
    #     self.ensure_one()
    #     # Based on "En caso de no contar con la hora se debe registrar 12:00:00"
    #     mxn = self.env.ref('base.MXN')
    #     precision_digits = self.env['decimal.precision'].precision_get('Account')
    #     date = datetime.combine(fields.Datetime.from_string(self.real_copper), datetime.strptime('12:00:00', '%H:%M:%S').time()).strftime('%Y-%m-%dT%H:%M:%S')

    #     rate = ('%0.*f' % (
    #         precision_digits,
    #         self.currency_id.with_context(date=self.payment_date).compute(
    #             1, mxn))) if self.currency_id.name != 'MXN' else False

    #     return {
    #         'mxn': mxn,
    #         'payment_date': date,
    #         'payment_rate': rate,
    #         'pay_vat_ord': False,
    #         'pay_account_ord': False,
    #         'pay_vat_receiver': False,
    #         'pay_account_receiver': False,
    #         'pay_ent_type': False,
    #         'pay_certificate': False,
    #         'pay_string': False,
    #         'pay_stamp': False,
    #     }


    def change_dates(self):

        for self_id in self:
            if self_id.partner_type == "customer":
                if self_id.real_copper:
                    self_id.payment_date = self_id.real_copper


    def get_format_date(self):
        date = datetime.combine(fields.Datetime.from_string(self.payment_date), datetime.strptime('12:00:00', '%H:%M:%S').time()).strftime('%Y-%m-%dT%H:%M:%S')
        return date