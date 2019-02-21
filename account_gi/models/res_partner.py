# -*- coding: utf-8 -*-
# © <2018> < ()>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
from datetime import datetime, date, time, timedelta
from odoo import fields, models, api

_logger = logging.getLogger(__name__)

class res_partner(models.Model):
    _inherit = 'res.partner'

    def get_account_average(self):
        for self_id in self:
            self_account = self.env['account.invoice'].search([('partner_id', '=', self_id.id),('type','=','out_invoice')])
        

            acom_average = 0
            for account_id in self_account:
                acom_average = acom_average + account_id.day_trans_payment

            if len(self_account):
                acom_average = acom_average / len(self_account)

            self_id.average_payment = acom_average

    average_payment = fields.Float(
        string='Promedio de pago',
        compute=get_account_average
    )