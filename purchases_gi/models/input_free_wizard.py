# -*- coding: utf-8 -*-
# © <2017> <Juan Carlos Vazquez Beas (jcvazquez@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from datetime import datetime, date, timedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT

import sys, logging
from openerp.osv import osv
from odoo import fields, models, api

_logger = logging.getLogger(__name__)

class input_free_wizard(models.TransientModel):
    """
    Se creó el Wizard para distinguir las pruebas gratis en inventarios.
    """
    _name = 'input.free.wizard'
    _description = 'INPUT FREE WIZARD'


    def get_id_stock(self):
        """
        Regresa el contexto actual.
        """       
        return self.env.context.get('active_id', False)

    def get_product_id(self):
        """
        Regresa el producto relacionado en el picking.
        """
        stock = self.env.context.get('active_id', False)
        stock_id = self.env['stock.picking'].sudo().search([('id', '=', stock)], limit=1)

        return stock_id.move_lines.product_id.id

    def get_product_uos(self):
        """
        Regresa la unidad de medida del producto.
        """
        stock = self.env.context.get('active_id', False)
        stock_id = self.env['stock.picking'].sudo().search([('id', '=', stock)], limit=1)
        return stock_id.move_lines.product_uos.id

    stock_id = fields.Many2one(
        string='Entrada (stock picking)',
        comodel_name='stock.picking',
        ondelete='cascade',
        auto_join=False,
        default=get_id_stock
    )

    product_id = fields.Many2one(
        string='Producto',
        comodel_name='product.product',
        required=True,
        default=get_product_id
    )

    product_uos = fields.Many2one(
        string='Unidad de medida',
        comodel_name='product.uom',
        required=True,
        default=get_product_uos
    )

    quantity = fields.Integer(
        string='Cantidad de producto',
        required=True
    )



    @api.multi
    def free_admission(self):
        """
        Crea entradas pickings y movimientos de productos gratis para identificarlos.
        """
        stock_move_id = self.env['stock.move'].create({
            'name': self.product_id.name,
            'product_id': self.product_id.id,
            'product_uom_qty': self.quantity,
            'product_uom': self.product_uos.id,
            'invoice_state': self.stock_id.move_lines.invoice_state,
            'date': date.today(),
            'date_expected': date.today(),
            'location_id': self.stock_id.move_lines.location_id.id,
            'location_dest_id': self.stock_id.move_lines.location_dest_id.id,
        })

        stock_picking_id = self.env['stock.picking'].create({
            'name': self.stock_id.name + " (Sin costo)",
            'partner_id': self.stock_id.partner_id.id,
            'backorder_id': self.stock_id.backorder_id.id,
            'company_id': self.stock_id.company_id.id,
            'move_type': self.stock_id.move_type,
            'invoice_state': self.stock_id.invoice_state,
            'picking_type_id': self.stock_id.picking_type_id.id,
            'group_id': self.stock_id.group_id.id,
            'priority': self.stock_id.priority,
            'purchase_order_id': self.stock_id.purchase_order_id.id,
            'origin': self.stock_id.origin,
            'date_done': date.today(),
            'purchase_ok': True,
            'it_free': True,
            'move_lines': [(4,stock_move_id.id)],
        })

        stock_picking_id.action_confirm()

        stock_picking_id.do_transfer()

        self.sudo().stock_id.purchase_order_id.picking_ids = [(4,stock_picking_id.id)]

        if self.stock_id.purchase_order_id.invoice_ids:

            _logger.warning(self.product_id.property_account_expense)
            _logger.warning(self.product_id.property_account_expense.name)
            _logger.warning(self.product_id.property_account_expense.id)
            _logger.warning(self.product_id.property_account_expense.code)
            if not self.product_id.property_account_expense:
                raise osv.except_osv('Advertencia','Se debe configurar la cuenta de gasto para el producto.')

            name = '['+str(self.product_id.default_code)+'] '+self.product_id.name+' (Producto sin precio)'

            account_line_id = self.env['account.invoice.line'].sudo().create({
                'name':name,
                'product_id':self.product_id.id,
                'date_planned':date.today(),
                'account_id': self.product_id.property_account_expense.id,
                'quantity':self.quantity,
                'uos_id':self.product_uos.id,
            })

            self.sudo().stock_id.purchase_order_id.invoice_ids.invoice_line = [(4,account_line_id.id)]
