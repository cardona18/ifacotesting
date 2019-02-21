# -*- coding: utf-8 -*-
# © <2016> <Luis Alfredo Valencia (lavalencia@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
from odoo import fields, models, api

_logger = logging.getLogger(__name__)


class PurchaseInmediateTransfer(models.TransientModel):
    _name = 'purchase.inmediate.transfer'
    _description = 'Immediate Transfer'

    purchase_ids = fields.Many2many(
        'purchase.requisition', 'purchase_transfer_rel'
        )
    comments = fields.Text(
        string='Comentarios'
    )

    def process(self):
        for purchase_id in self.purchase_ids:
            purchase_id.state = 'partially_authorized'
            purchase_id.request_purchanse_authorization(
                transfer_inmediate=True
                )

    def cancel_line(self):
        for purchase_id in self.purchase_ids:
            for line_id in purchase_id.line_ids:
                if not line_id.order_ids:
                    line_id.state = 'cancel'
            purchase_id.state = 'authorizes'
            purchase_id.request_purchanse_authorization(
                transfer_inmediate=True
                )

    def cancel_line_process(self):
        for purchase_id in self.purchase_ids:
            for line_id in purchase_id.line_ids:
                if not line_id.order_ids:
                    line_id.state = 'cancel'
            purchase_id.comment_cancel = self.comments
            purchase_id.action_cancel(context=True)

