# -*- coding: utf-8 -*-
# © <2016> <Juan Carlos VB (jcvazquez@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import date
import sys, logging
from odoo import fields, models, api
from openerp.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class purchase_requisition_line_gi(models.Model):
    """
    Hereda el modelo de lineas de compra y le agrega funcionalidades necesarias para la lógica del negocio.
    """
    _inherit = 'purchase.requisition.line'


    def order_returns(self):
        """
        Devuelve el id de la compra
        """
        for self_id in self:
            self_id.purchase_ids = self_id.requisition_id.purchase_ids

    def get_product_qty_quoted(self):
        """
        Obtiene el total cotizado por producto.
        """
        for self_id in self:
            accom_qty = 0
            if self_id.order_ids:
                for order_id in self_id.order_ids:
                    line_product = self.env['purchase.order.line'].search(
                        [('order_id', '=', order_id.id), ('product_id', '=', self_id.product_id.id),
                         ('account_analytic_id', '=', self_id.account_analytic_id.id)])

                    for line_prod in line_product:

                        if line_prod.priceless == False and line_prod.additional_costs ==  False:
                            accom_qty = accom_qty + line_prod.product_qty

                self_id.product_qty_quoted = accom_qty



    product_id = fields.Many2one(
        'product.product',
        string='Producto',
        track_visibility='onchenge'
    )
    product_qty = fields.Float(
        string='Cantidad',
        track_visibility="onchenge"
    )
    product_uom_id = fields.Many2one(
        'product.uom',
        string='Unidad de medida',
        track_visibility='onchenge',
        readonly=False, 
    )
    purchase_ids = fields.One2many(
        'purchase.order',
        'requisition_id',
        string='Purchase Orders', 
        compute=order_returns
    )
    order_ids = fields.Many2many(
        'purchase.order',
        string='Cotización',
    )
    product_qty_quoted = fields.Float(
        string='Total cotizado',
        compute=get_product_qty_quoted, digits=[12, 3]
    )
    state = fields.Selection(
        [('draft', 'Pendiente'),
         ('done', 'Autorizado'),
         ('cancel', 'Cancelado')],
        string='Estado',
        default='draft',
    )

    @api.multi
    def write(self,vals):
        """
        Agrega la unidad de medida al escribir el registro.
        """
        res = super(purchase_requisition_line_gi, self).write(vals)

        if 'product_id' in vals:
            self.product_uom_id = self.product_id.uom_po_id.id




    @api.model
    def create(self, vals):
        """
        Agrega la unidad de medida al crear el registro.
        """
        res = super(purchase_requisition_line_gi, self).create(vals)
        if 'product_id' in vals:
            product = self.env['product.product'].sudo().search([('id', '=', vals['product_id'])], limit=1)
            res['product_uom_id'] = product.uom_po_id.id
        if 'state' not in vals:
            vals['state'] = 'draft'

    description_product = fields.Text(string='Descripción')

    @api.onchange('product_id')
    def onchange_product_id(self):
        """
        Muestra un mensaje del formato 'Requerimientos de usuario'
        """
        if self.product_id:
            self.description_product = self.product_id.display_name

