# -*- coding: utf-8 -*-
# © <2018> < ()>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
from datetime import datetime, date, time, timedelta
from odoo import fields, models, api
from numpy import *

_logger = logging.getLogger(__name__)


class account_invoice_gi(models.Model):
    _inherit = 'account.invoice'

    def get_expiration_days(self):
        self_account = self.env['account.invoice'].search([('state', 'not in', ['cancel','paid'])])

        total_days = None

        for self_id in self_account:
            if self_id.date_due:
                total_days = date.today() - datetime.strptime(self_id.date_due, '%Y-%m-%d').date()
                self_id.expiration_days = total_days.days

    def get_trans_payment(self):

        self_account = self.env['account.invoice'].search([('type','=','out_invoice')])

        for self_id in self_account:


            if not self_id.payment_ids:
                self_id.day_trans_payment = 0

            else:
                for self_payment_id in self_id.payment_ids:
                    format_date = "%Y-%m-%d"
                    date_comparation = 0
                    if self_id.payment_ids:
                        for self_dates in self_id.payment_ids:
                            if self_payment_id.payment_date >= self_dates.payment_date:
                                if self_id.delivery_date:
                                    date_comparation = date_comparation + 1
                                else:
                                    self_id.day_trans_payment = 0


                            if date_comparation == len(self_id.payment_ids):
                                days_tras_pay =  datetime.strptime(self_payment_id.payment_date, format_date) - datetime.strptime(self_id.delivery_date, format_date)
                                self_id.day_trans_payment = days_tras_pay.days
                    else:
                        self_id.day_trans_payment = 0


    def update_currency_rates(self):
        self_account = self.env['res.company'].search([('vat','!=', None)])

        for self_account_id in self_account:
            self_account_id.update_currency_rates()

    def get_aver_pay_part(self):

        self_account = self.env['account.invoice'].search([('type', '=', 'out_invoice'), ('state', '=', 'paid')])

        for self_id in self_account:
            partner_ids = self.env['account.invoice'].search([('partner_id', '=', self_id.partner_id.id), ('state', '=', 'paid')])

            _logger.warning(self_id.name)
            _logger.warning(len(partner_ids))
            average = self_id.day_trans_payment / len(partner_ids)
            self_id.aver_pay_part = average

    def _get_c_ecchange(self):

        reception = self.env['purchase.reception'].search([('order_id', '=', self.order_id.id)], limit=1)

        if reception:
            self.exchang = reception.exchangerate



    def get_exchangerate(self):

        for self_id in self:
            rate = self.env['purchase.reception'].search([('order_id', '=', self_id.order_id.id)], limit=1)

            if rate:
                self_id.c_exchang = rate.c_exchangerate
                _logger.warning(rate.c_exchangerate)
                return rate.c_exchangerate

    num_request = fields.Char(
        string='Numero de contra recibo',
    )
    expiration_days = fields.Integer(
        string='Días de vencido',
    )
    day_trans_payment = fields.Integer(
        string='Días trascurridos del pago',
    )
    aver_pay_part = fields.Float(
        string='Promedio de pago',
    )
    c_exchang = fields.Char(
        string='Tipo de cambio al dia de la orden de compra',
        compute='get_exchangerate',
    )
    exchang = fields.Char(
        string='Tipo de cambio',
        compute='_get_c_ecchange',

    )



    def l10n_mx_edi_update_sat_status_gi(self):
        self.date_invoice = date.today()
        _logger.warning(self.date_invoice)
        _logger.warning(self.date_invoice)
        _logger.warning(self.date_invoice)
        _logger.warning(self.date_invoice)
        _logger.warning(self.date_invoice)
        self.l10n_mx_edi_update_pac_status()


    def action_invoice_open_gi(self):
        self.date_invoice = datetime.now()
        return self.action_invoice_open()
