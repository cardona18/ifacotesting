# -*- coding: utf-8 -*-
# © <2016> <Juan Carlos Vazquez Beas (jcvazquez@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging

from odoo import api, fields, models, _

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

    cancel_commentary = fields.Char(
        string='Comentario de cancelación',
        store='True',
    )

    cancel_type = fields.Many2one(
        string='Tipo de cancelación',
        comodel_name='account_res_cancel_types',
        required='True',
        store='True',
    )

    cause = fields.Char(
        string='Motivo',
        store='True',
    )

    def action_invoice_cancel_gi(self):
        self.account_id.message_post('Se cancelado la factura por el siguiente motivo: ' + self.cause)
        self.account_id.comentario_cancel = self.cancel_commentary
        self.account_id.tipo_cancel = self.cancel_type
        self.account_id.motivo_cancel = self.cause
        self.account_id.action_invoice_cancel_gi()
