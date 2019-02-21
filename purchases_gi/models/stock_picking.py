# -*- coding: utf-8 -*-
# © <2017> <Juan Carlos Vazquez Beas (jcvazquez@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from datetime import datetime
import sys, logging
from odoo import fields, models, api

_logger = logging.getLogger(__name__)


class stock_picking(models.Model):
    """
    Se heredó stock.picking para agregar campos necesarios en compras.
    """
    _inherit = 'stock.picking'


    purchase_ok = fields.Boolean(
        string='Fue creado desde una compra',
    )

    it_free = fields.Boolean(
        string='Sin costo',
    )

    purchase_order_id = fields.Many2one(
        string='Orden de compra',
        comodel_name='purchase.order',
        ondelete='cascade',
    )

    r_seq_order = fields.Char(
        string='Orden de compra',
        related='purchase_order_id.sequence_order',
    )

    r_currency_id = fields.Many2one(
        string='Moneda ',
        related="purchase_order_id.currency_id"
    )

    r_notes = fields.Text(
        string='Observaciones ',
        related="purchase_order_id.notes"
    )

    lot = fields.Char(
        string='Lote',
    )

    type_od_document = fields.Selection(
        string='Tipo de documento',
        required=False,
        readonly=False,
        index=False,
        default=False,
        help=False,
        selection=[
                    ('bill', 'Factura borrador'),
                    ('remission', 'Remisión')
                ]
    )

    num_of_doc = fields.Integer(
        string='Número del documento',
        required=False,
        readonly=False,
        index=False,
        default=0,
        help=False
    )

    invoice_ids = fields.Many2many(
        string='Facturas',
        comodel_name='account.invoice',
    )

    date_planned = fields.Date(
        string='Fecha planificada',
        default=datetime.today(),
        required=False,
    )


