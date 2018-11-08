# -*- coding: utf-8 -*-
# © <2016> <Juan Carlos VB (jcvazquez@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import sys, logging
from time import time
from openerp.osv import osv
from odoo import fields, models, api
from odoo.tools.float_utils import float_is_zero, float_compare
from openerp.exceptions import ValidationError
from .utils import redondear_cantidad_decimales
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

_logger = logging.getLogger(__name__)

class purchase_order_line(models.Model):
    """
    Se heredó la clase lineas de compra para adecuar la funcionalidad requerida y se agregaron campos y funciones. 
    """
    _inherit = 'purchase.order.line'
    _description = 'PURCHASE ORDER LINE'

    _sql_constraints = []


    def get_current_company_id(self):
        """
        Regresa la compañia del usuario actual.
        """
        return self.env.user.company_id.id

    order_id_related = fields.Many2one(
        string='Solicitud vinculada',
        comodel_name='purchase.order',
    )
    r_orden_id = fields.Char(
        related='order_id_related.sequence_order',
        string='Orden',
        store=True
    )
    delivered = fields.Integer(
        string='Entregado',
    )
    remaining = fields.Integer(
        string='Restante',
    )
    price_unit_no_discount = fields.Float(
        string='Precio unitario',
        digits=(16, 2),
        default=0.0,
    )
    discount = fields.Float(
        string='Descuento (%)',
    )
    r_purchase_requ_id = fields.Many2one(
        related='order_id_related.requisition_id',
        string='Solicitud compra',
        store=True,
    )
    price_unit = fields.Float(
        string='Precio neto',
        required=False,
        default=0.0,
        digits=(16, 2),
        store=1,
    )
    date_planned = fields.Date(
        string='Fecha planificada',
        required=False,
    )

    state_line_order = fields.Selection(
        [('draft', 'En borrador'),
        ('with_quote', 'Con cotización'),
        ('related', 'Relacionada'),
        ('orden_complete', 'Completada'),
        ('cancel', 'Cancelada')], 
        string='Estado',
        default='draft'
    )
    company_id = fields.Many2one(
        string='Empresa solicitante',
        comodel_name='res.company',
        default=get_current_company_id
    )
    priceless = fields.Boolean(
        string='Sin precio',
    )
    additional_costs = fields.Boolean(
        string='Costo adicional ',
    )


    @api.onchange('priceless')
    def onchange_priceless(self):
        """
        Quita el precio unitario 
        """
        if self.priceless:
            self.price_unit = 0.0
    

    @api.multi
    def create_stock_moves_gi(self, picking):
        "Devuelve los movimientos por linea"
        moves = self.env['stock.move']
        done = self.env['stock.move'].browse()
        for line in self:
            for val in line.prepare_stock_moves_gi(picking):
                done += moves.create(val)
        return done



    @api.multi
    def prepare_stock_moves_gi(self, picking):
        """ Prepare the stock moves data for one order line. This function returns a list of
        dictionary ready to be used in stock.move's create()
        """
        self.ensure_one()
        res = []
        if self.product_id.type not in ['product', 'consu']:
            return res
        qty = 0.0
        price_unit = self._get_stock_move_price_unit()
        for move in self.move_ids.filtered(lambda x: x.state != 'cancel' and not x.location_dest_id.usage == "supplier"):
            qty += move.product_qty
        template = {
            'name': self.name or '',
            'product_id': self.product_id.id,
            'product_uom': self.product_uom.id,
            'date': self.order_id.date_order,
            'date_expected': self.date_planned,
            'location_id': self.order_id.partner_id.property_stock_supplier.id,
            'location_dest_id': self.order_id._get_destination_location(),
            'picking_id': picking.id,
            'partner_id': self.order_id.dest_address_id.id,
            'move_dest_ids': [(4, x) for x in self.move_dest_ids.ids],
            'state': 'draft',
            'purchase_line_id': self.id,
            'company_id': self.order_id.company_id.id,
            'price_unit': price_unit,
            'picking_type_id': self.order_id.picking_type_id.id,
            'group_id': self.order_id.group_id.id,
            'origin': self.order_id.name,
            'route_ids': self.order_id.picking_type_id.warehouse_id and [(6, 0, [x.id for x in self.order_id.picking_type_id.warehouse_id.route_ids])] or [],
            'warehouse_id': self.order_id.picking_type_id.warehouse_id.id,
        }

        template['product_uom_qty'] = self.product_qty
        res.append(template)
        return res

    @api.depends('discount')
    def _compute_amount(self):
        """
        Sobre escribo el metodo que calcula el subtotal para adaptarlo al aplicarle el descuento
        """
        for line in self:
            price_unit = False
            price = line._get_discounted_price_unit()
            if price != line.price_unit:
                taxes = line.taxes_id.compute_all(price, line.order_id.currency_id, line.product_qty,
                                                  product=line.product_id, partner=line.order_id.partner_id)
            else:
                taxes = line.taxes_id.compute_all(line.price_unit, line.order_id.currency_id, line.product_qty,
                                                 product=line.product_id, partner=line.order_id.partner_id)
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })
            if price_unit:
                line.price_unit = price_unit

    def _get_discounted_price_unit(self):
        """
        Metodo para obtener el descuento por el precio unitario
        """
        self.ensure_one()
        if self.discount:
            return self.price_unit * (1 - self.discount / 100)
        return self.price_unit

    @api.constrains('account_analytic_id')
    def _checl_account_analytic_id(self):
        if not self.account_analytic_id:
            raise ValidationError('No ha capturado la cuenta analitica en las lineas del producto {}.'.format(self.product_id.display_name))

    # Permite modifcar ordenes
    # change_purchase = fields.Boolean('Modificar datos de orden de compra', related='order_id.change_purchase')

    @api.onchange('product_qty', 'product_uom')
    def _onchange_quantity(self):
        if not self.product_id:
            return

        seller = self.product_id._select_seller(
            partner_id=self.partner_id,
            quantity=self.product_qty,
            date=self.order_id.date_order and self.order_id.date_order[:10],
            uom_id=self.product_uom)

        if seller or not self.date_planned:
            self.date_planned = self._get_date_planned(seller).strftime(DEFAULT_SERVER_DATETIME_FORMAT)

        if not seller:
            return

        price_unit = self.env['account.tax']._fix_tax_included_price_company(seller.price,
                                                                             self.product_id.supplier_taxes_id,
                                                                             self.taxes_id,
                                                                             self.company_id) if seller else 0.0
        if price_unit and seller and self.order_id.currency_id and seller.currency_id != self.order_id.currency_id:
            price_unit = seller.currency_id.compute(price_unit, self.order_id.currency_id)

        if seller and self.product_uom and seller.product_uom != self.product_uom:
            price_unit = seller.product_uom._compute_price(price_unit, self.product_uom)

        #Comente linea para que  no cambie el precio unitario
        #self.price_unit = price_unit