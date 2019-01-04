# -*- coding: utf-8 -*-
# © <2016> <Juan Carlos Vazquez Beas (jcvazquez@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
from odoo import fields, models

_logger = logging.getLogger(__name__)

class cancel_account_invoice(models.TransientModel):
    _name = 'cancel.account.invoice'
    _description = "Motivo de cancelación"

    def act_cancel_invoice(self):
        return self.env.context.get('active_id', False)

    account_id = fields.Many2one(
        string='Factura',
        comodel_name='account.invoice',
        default=act_cancel_invoice
    )

    commentary = fields.Html(
        string='Motivo de la cancelación',
    )

    def action_invoice_cancel_gi(self):
        self.account_id.message_post('Se cancelado la factura por el siguiente motivo: ' + self.commentary)
        # self.account_id.action_invoice_cancel()

        result = super(account_invoice_gi, self).action_invoice_cancel()
        for record in self.filtered(lambda r: r.l10n_mx_edi_is_required()):
            record._l10n_mx_edi_cancel()
        return result
