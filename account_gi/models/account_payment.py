# -*- coding: utf-8 -*-
# © <2018> < ()>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
from datetime import datetime, date, time, timedelta
from odoo import fields, models, api

_logger = logging.getLogger(__name__)


class account_payment_gi(models.Model):
    _inherit = 'account.payment'

    def to_cancel_payment(self):
        self.l10n_mx_edi_pac_status = 'to_cancel'
        
        
    def _compute_status_to_cancel(self):
        for rec in self:
            if rec.state == 'cancelled' and rec.l10n_mx_edi_pac_status == 'signed':
                rec.status_to_cancel = True
            else:
                rec.status_to_cancel = False
                
        
    status_to_cancel = fields.Boolean(default=False, compute=_compute_status_to_cancel)
