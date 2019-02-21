# -*- coding: utf-8 -*-
# © <2018> < ()>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
from odoo.tests import common
from datetime import datetime, date, time, timedelta


_logger = logging.getLogger(__name__)

class test_account_invoice_gi(common.TransactionCase):

    def setup(self):
        super(test_account_invoice_gi, self).setUp()

    def test_account_invoice(self):
        """
        Prueba que se pueda crear la factura. 
        """
        partner_id = self.env['res.partner'].search([],limit=1)

        self_acc = self.env['account.invoice'].create({
                'name': 'Prueba',
                'partner_id': partner_id.id,
                'num_request': 'Prueba',
                'expiration_days': 1,
                'day_trans_payment': 2,
                'aver_pay_part': 1.5,
                'state': 'draft',
        })

        self_acc.l10n_mx_edi_update_sat_status_gi()

        self.assertNotEqual(self_acc.id, None)



    def test_cancel_account_invoice(self):
        """
        Prueba que se pueda cancelar la factura.
        """
        acco_invoice = self.env['account.invoice'].search([],limit=1)

        self_acc = self.env['cancel.account.invoice'].create({
                'account_id': acco_invoice.id,
                'commentary': 'Esta es una prueba',
        })

        self_acc.wizard_action()

        self.assertEqual(self_acc.account_id.state, 'cancel')




    def test_average_account_invoice(self):
        """
        Prueba que se calcule el promedio de pago. 
        """
        partner_id = self.env['res.partner'].search([],limit=1)

        partner_id.get_account_average()

        self.assertEqual(partner_id.get_account_average(), 0)

