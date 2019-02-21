# -*- coding: utf-8 -*-
# © <2016> <Juan Carlos VB (jcvazquez@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import sys, logging
from odoo import fields, models, api

_logger = logging.getLogger(__name__)

class cancel_purchase_requisition(models.TransientModel):
    """
     Se creó este wizard para agregar un comentario que justifique la cancelación de una solicitud de compra.
    """
    _name = 'cancel.purchase.requisition'


    def act_cancel_purchase(self):
        """
        Regresa el contexto actual.
        """        
        return self.env.context.get('active_id', False)

    purchase_req_id = fields.Many2one(
        string='Solicitud de compra',
        comodel_name='purchase.requisition',
        default=act_cancel_purchase
    )
    comments = fields.Text(
        string='Comentarios'
    )

    @api.multi
    def cancel_purchase_requisit(self):
        """
        Cancela la solicitud de compra y graba el comentario.
        """
        for line_id in self.purchase_req_id.line_ids:
            if line_id.order_ids:
                line_id.order_ids.sudo().button_cancel()
            line_id.state = 'cancel'
        self.purchase_req_id.sudo().state = 'cancel'
        self.purchase_req_id.sudo().comment_cancel = self.comments
