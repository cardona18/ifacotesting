# -*- coding: utf-8 -*-
# © <2018> < ()>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
from odoo import fields, models, api

_logger = logging.getLogger(__name__)


class account_invoice_gi(models.Model):
    _inherit = 'account.invoice'

    def get_group(self):
        self.perm_payment = self.env.user.has_group('payment_schedule_gi.group_payment_schedule')

    payment_schedule_date = fields.Date(
        string='Fecha programada de pago',
        track_visibility='onchange',
    )
    perm_payment = fields.Boolean(
        string='Con permisos de programar pagos',
        compute=get_group,
    )