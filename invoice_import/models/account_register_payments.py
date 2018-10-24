# -*- coding: utf-8 -*-
# © <2018> < ()>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
from odoo import fields, models, api

_logger = logging.getLogger(__name__)

class AccountRegisterPaymentsWizard_gi(models.TransientModel):
    _inherit = 'account.register.payments'

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


    def create_payments(self):
        if self.payment_method_code == 'sdd':
            rslt = self.env['account.payment']


            for invoice in self.invoice_ids:
                mandate = invoice._get_usable_mandate()
                if not mandate:
                    raise UserError(_("This invoice cannot be paid via SEPA Direct Debit, as there is no valid mandate available for its customer at its creation date."))
                rslt += invoice.pay_with_mandate(mandate)
            return rslt

        return super(AccountRegisterPaymentsWizard_gi, self).create_payments()



    def get_format_date(self):
        date = datetime.combine(fields.Datetime.from_string(self.real_copper), datetime.strptime('12:00:00', '%H:%M:%S').time()).strftime('%Y-%m-%dT%H:%M:%S')
        return date