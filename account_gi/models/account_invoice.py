# -*- coding: utf-8 -*-
# © <2018> < ()>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
from datetime import datetime, date, time, timedelta
from odoo import fields, models, api, _
from odoo.addons.account.models.account_invoice import TYPE2REFUND

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

        for self_id in self:
            reception = self.env['purchase.reception'].search([('order_id', '=', self_id.order_id.id)], limit=1)

            if reception:
                self_id.exchang = reception.exchangerate
                _logger.warning(reception.exchangerate)



    def get_exchangerate(self):

        for self_id in self:
            _logger.warning(self_id.order_id.id)
            _logger.warning(self_id.origin)
            rate = self.env['purchase.reception'].search([('order_id', '=', self_id.order_id.id)], limit=1)


            if rate:
                self_id.c_exchang = rate.c_exchangerate
                _logger.warning(rate.c_exchangerate)
                return rate.c_exchangerate
            else:
                rate = self.env['purchase.reception'].search([('name', '=', self_id.origin)], limit=1)
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
    comments = fields.Text(
        string='Comentarios',
    )
    reason_type = fields.Integer(
        string='ID Tipo de razon',
    )

    reason = fields.Char(
        string='Tipo de razon',
        compute='_get_reason'
    )

    comentario_cancel = fields.Text(
        string='Comentarios de cancelación',
        readonly=True,
    )

    tipo_cancel = fields.Integer(
        string='ID Tipo de cancelación',
        readonly=True,
    )

    cancel_reason = fields.Text(
        string='Tipo de cancelación',
        compute='_get_cancel_reason',
        readonly=True,
    )

    motivo_cancel = fields.Text(
        string='Motivo de cancelación',
        readonly=True,
    )

    def _get_cancel_reason(self):
        for self_id in self:
            can_rea = self.env['account_res_cancel_types'].search([('id', '=', self_id.tipo_cancel)], limit=1)
            self_id.cancel_reason=can_rea.name
            return can_rea.name

    def _get_reason(self):
        for self_id in self:
            rea = self.env['account.res_reasons_types'].search([('id', '=', self_id.reason_type)], limit=1)
            self_id.reason=rea.name
            return rea.name

    @api.multi
    @api.returns('self')
    def refund(self, date_invoice=None, date=None, description=None, journal_id=None, comment=None, reason=None):
        new_invoices = self.browse()
        for invoice in self:
            # create the new invoice
            values = self._prepare_refund(invoice, date_invoice=date_invoice, date=date,
                                    description=description, journal_id=journal_id, comment=comment, reason=reason)
            refund_invoice = self.create(values)
            invoice_type = {'out_invoice': ('customer invoices credit note'),
                'in_invoice': ('vendor bill credit note')}
            message = _("This %s has been created from: <a href=# data-oe-model=account.invoice data-oe-id=%d>%s</a>") % (invoice_type[invoice.type], invoice.id, invoice.number)
            refund_invoice.message_post(body=message)
            new_invoices += refund_invoice
        return new_invoices

    @api.model
    def _prepare_refund(self, invoice, date_invoice=None, date=None, description=None, journal_id=None, comment=None, reason=None):
        """ Prepare the dict of values to create the new credit note from the invoice.
            This method may be overridden to implement custom
            credit note generation (making sure to call super() to establish
            a clean extension chain).

            :param record invoice: invoice as credit note
            :param string date_invoice: credit note creation date from the wizard
            :param integer date: force date from the wizard
            :param string description: description of the credit note from the wizard
            :param integer journal_id: account.journal from the wizard
            :return: dict of value to create() the credit note
        """
        values = {}
        for field in self._get_refund_copy_fields():
            if invoice._fields[field].type == 'many2one':
                values[field] = invoice[field].id
            else:
                values[field] = invoice[field] or False

        values['invoice_line_ids'] = self._refund_cleanup_lines(invoice.invoice_line_ids)

        tax_lines = invoice.tax_line_ids
        values['tax_line_ids'] = self._refund_cleanup_lines(tax_lines)

        if journal_id:
            journal = self.env['account.journal'].browse(journal_id)
        elif invoice['type'] == 'in_invoice':
            journal = self.env['account.journal'].search([('type', '=', 'purchase')], limit=1)
        else:
            journal = self.env['account.journal'].search([('type', '=', 'sale')], limit=1)
        values['journal_id'] = journal.id

        values['type'] = TYPE2REFUND[invoice['type']]
        values['date_invoice'] = date_invoice or fields.Date.context_today(invoice)
        values['state'] = 'draft'
        values['number'] = False
        values['origin'] = invoice.number
        values['payment_term_id'] = False
        values['refund_invoice_id'] = invoice.id

        if date:
            values['date'] = date
        if description:
            values['name'] = description
        if comment:
            values['comments'] = comment
        if reason:
            values['reason_type'] = reason

        return values

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
