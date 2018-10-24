# -*- coding: utf-8 -*-
# © <2017> <Omar Torres Silva (otorres@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from datetime import timedelta
from dateutil import parser
import locale
import logging
import math

from odoo import api, fields, models, http

_logger = logging.getLogger(__name__)

class stock_picking_gi(models.Model):
    _inherit = 'stock.picking'

    shipment_cfdi_id = fields.Many2one(
        string='CFDI Traslado',
        comodel_name='account.invoice'
    )
    invoice_cfdi_id = fields.Many2one(
        string='Factura',
        comodel_name='account.invoice'
    )
    label_ids = fields.One2many(
        string='Etiquetas',
        comodel_name='stock.shipping.label',
        inverse_name='picking_id'
    )
    labels_count = fields.Integer(
        string='Etiquetas',
        compute='_labels_count',
    )
    sale_shipment = fields.Boolean(
        string='Entrega de venta',
        compute='compute_sale_shipment'
    )
    delivery_date = fields.Datetime(
        string='Fecha de entrega'
    )
    shipping_guide_id = fields.Many2one(
        string='Guia de embarque',
        comodel_name='sale.shipping.guide'
    )
    operation_type = fields.Selection(
        string='Tipo de operación',
        related='picking_type_id.code',
        selection=[
            ('incoming', 'Proveedores'),
            ('outgoing', 'Clientes'),
            ('internal', 'Interno'),
            ('mrp_operation', 'Fabricación')
        ]
    )

    def _labels_count(self):
        """
            Count all stock.shipping.label related records
        """

        for item in self:
            item.labels_count = len(item.sudo().label_ids)

    @api.multi
    def compute_sale_shipment(self):

        for picking in self:
            picking.sale_shipment = picking.state == 'done' and picking.picking_type_id.code == 'outgoing' and picking.sale_id.id


    @api.multi
    def shipment_invoices(self, is_shipment = False):


        _logger.warning("Holaaaaaaa")

        for picking in self:

            if not picking.sale_shipment:
                continue

            if picking.shipment_cfdi_id.id and is_shipment:
                continue

            if picking.invoice_cfdi_id.id and not is_shipment:
                continue

            picking.make_picking_invoice(is_shipment)

        for picking in self:

            _logger.warning("Hola mundo")

            if picking.picking_type_id.transfer:


                _logger.warning(self.company_id)
                picking.origin = self.name
                picking.picking_type_code = 'outgoing'
                picking.picking_type_code = 'outgoing'

                _logger.warning("Que valor tiene esta cosa")
                _logger.warning(picking.picking_type_code)

                partner_id = self.env['res.partner'].sudo().search([('name', '=', picking.company_id.name)], limit=1)
                picking.partner_id = partner_id.id

                picking.type = 'out_invoice'


                _logger.warning("--------------> "+ picking.partner_id.name)


                picking.date_invoice = self.env['l10n_mx_edi.certificate'].sudo().get_mx_current_datetime().date()
                picking.fiscal_position_id = self.company_id.partner_id.property_account_position_id.id
                picking.l10n_mx_edi_usage = self.sale_id.partner_id.sale_invoice_usage or 'P01'
          

                _logger.warning("TRuena al llamar al metodo")

                _logger.warning(is_shipment)
                self.sale_shipment = True


                res = picking.make_picking_invoice_from_stock(is_shipment)

                _logger.warning("REsultado...............")
                _logger.warning("REsultado...............")
                _logger.warning("REsultado...............")
                _logger.warning(res)

    def make_picking_invoice_from_stock(self, is_shipment = False):

        self.ensure_one()

        _logger.warning("Entro a funcion 'make_picking_invoice_from_stock'")

        company_id = self.company_id
        invoice_values = {
            'origin': self.name,
            'company_id': company_id.id,
            'partner_id': self.partner_id.id,
            'order_num': self.name,
            # 'payment_term_id': self.payment_term_id.id,
            'partner_shipping_id': self.partner_id.id,
            'date_invoice': self.env['l10n_mx_edi.certificate'].sudo().get_mx_current_datetime().date(),
            'type': 'out_invoice',
            'fiscal_position_id': company_id.partner_id.property_account_position_id.id,
            'l10n_mx_edi_usage': self.partner_id.sale_invoice_usage or 'P01',
            'shipment_invoice': is_shipment,
        }

        if is_shipment:
            invoice_values['payment_term_id'] = False

        invoice = self.env['account.invoice'].create(invoice_values)

        _logger.warning("Factura-----------------> :D")
        _logger.warning(invoice)

        self.shipment_cfdi_id = invoice.id

        for line in self.move_lines:

            if not is_shipment and not line.sale_line_id.id:
                continue

            line_annex = ''

            for lot_line in line.move_line_ids:

                line_annex += '\nLote: %s %.3f ENV: %s\n%s%s%s%s%s%s' % (
                    lot_line.lot_id.name,
                    lot_line.qty_done,
                    line.product_uom.name,
                    'F.Cad: %s' % self.locale_date_format_vig(lot_line.lot_id.life_date, '%b/%y').capitalize() if lot_line.lot_id.life_date else '',
                    '\n' if lot_line.lot_id.life_date and not lot_line.lot_id.make_date else '',
                    ', ' if lot_line.lot_id.life_date and lot_line.lot_id.make_date else '',
                    'F.Fab. %s' %  self.upper_index(self.locale_date_format(lot_line.lot_id.make_date, '%d/%b/%y'), [3]) if lot_line.lot_id.make_date else '',
                    '\n' if lot_line.lot_id.life_date and lot_line.lot_id.make_date else '',
                    '(ENTREGA DE %s)' % self.locale_date_format(self.scheduled_date, '%B %d, %Y')
                )

            line_values = {
                'invoice_id': invoice.id,
                'account_id': line.product_id.property_account_income_id.id or line.product_id.categ_id.property_account_income_categ_id.id,
                'product_id': line.product_id.id,
                'name': (line.product_id.description_sale or line.product_id.name) + line_annex,
                'quantity': line.product_uom_qty,
                'price_unit': 0 if is_shipment else line.sale_line_id.price_unit,
                'uom_id': line.product_uom.id,
                'origin': self.name,
                'product_cbss': line.product_id.cbss
            }

            line_values['invoice_line_tax_ids'] = False if is_shipment else [(6, 0, line.sale_line_id.tax_id.ids)]

            inv_line = self.env['account.invoice.line'].create(line_values)

            if not is_shipment:
                line.sale_line_id.invoice_lines = [(4, inv_line.id, 0)]

        if is_shipment:
            self.shipment_cfdi_id = invoice.id
        else:
            self.invoice_cfdi_id = invoice.id
            invoice.compute_taxes()




    def make_picking_invoice(self, is_shipment = False):

        self.ensure_one()

        company_id = self.company_id
        invoice_values = {
            'origin': self.name,
            'company_id': company_id.id,
            'partner_id': self.sale_id.partner_id.id,
            'order_num': self.sale_id.client_order_ref,
            'payment_term_id': self.sale_id.payment_term_id.id,
            'partner_shipping_id': self.partner_id.id,
            'date_invoice': self.env['l10n_mx_edi.certificate'].sudo().get_mx_current_datetime().date(),
            'type': 'out_invoice',
            'fiscal_position_id': company_id.partner_id.property_account_position_id.id,
            'l10n_mx_edi_usage': self.sale_id.partner_id.sale_invoice_usage or 'P01',
            'shipment_invoice': is_shipment,
            'team_id': self.sale_id.team_id.id,
            'user_id': self.sale_id.user_id.id
        }

        if is_shipment:
            invoice_values['payment_term_id'] = False

        invoice = self.env['account.invoice'].create(invoice_values)

        for line in self.move_lines:

            if not is_shipment and not line.sale_line_id.id:
                continue

            line_annex = ''

            for lot_line in line.move_line_ids:

                line_annex += '\nLote: %s %.3f ENV: %s\n%s%s%s%s%s%s' % (
                    lot_line.lot_id.name,
                    lot_line.qty_done,
                    line.product_uom.name,
                    'F.Cad: %s' % self.locale_date_format_vig(lot_line.lot_id.life_date, '%b/%y').capitalize() if lot_line.lot_id.life_date else '',
                    '\n' if lot_line.lot_id.life_date and not lot_line.lot_id.make_date else '',
                    ', ' if lot_line.lot_id.life_date and lot_line.lot_id.make_date else '',
                    'F.Fab. %s' %  self.upper_index(self.locale_date_format(lot_line.lot_id.make_date, '%d/%b/%y'), [3]) if lot_line.lot_id.make_date else '',
                    '\n' if lot_line.lot_id.life_date and lot_line.lot_id.make_date else '',
                    '(ENTREGA DE %s)' % self.locale_date_format(self.scheduled_date, '%B %d, %Y')
                )

            line_values = {
                'invoice_id': invoice.id,
                'account_id': line.product_id.property_account_income_id.id or line.product_id.categ_id.property_account_income_categ_id.id,
                'product_id': line.product_id.id,
                'name': (line.product_id.description_sale or line.product_id.name) + line_annex,
                'quantity': line.product_uom_qty,
                'price_unit': 0 if is_shipment else line.sale_line_id.price_unit,
                'uom_id': line.product_uom.id,
                'origin': self.name,
                'product_cbss': line.product_id.cbss
            }

            line_values['invoice_line_tax_ids'] = False if is_shipment else [(6, 0, line.sale_line_id.tax_id.ids)]

            inv_line = self.env['account.invoice.line'].create(line_values)

            if not is_shipment:
                line.sale_line_id.invoice_lines = [(4, inv_line.id, 0)]

        if is_shipment:
            self.shipment_cfdi_id = invoice.id
        else:
            self.invoice_cfdi_id = invoice.id
            invoice.compute_taxes()

    @api.multi
    def action_create_labels(self):
        """
            Create shipping labels for each package
        """

        locale.setlocale(locale.LC_TIME, 'es_MX.UTF-8')

        for picking in self:

            if not picking.sale_shipment:
                continue

            picking.label_ids.unlink()

            for move_line in picking.move_lines:

                pack_qty = move_line.sale_line_id.product_packaging.qty

                for line in move_line.move_line_ids:

                    labels_ref = self.env['stock.shipping.label']
                    num_packs = math.floor(line.qty_done / pack_qty) if pack_qty > 0 else 0
                    qty_rest = line.qty_done % pack_qty if pack_qty > 0 else line.qty_done
                    life_date = parser.parse(line.lot_id.life_date) if line.lot_id.life_date else False
                    labels_count = num_packs + 1 if qty_rest > 0 else num_packs
                    life_date = life_date - timedelta(hours=5)

                    for label in range(0, int(num_packs)):
                        labels_ref.create({
                            'name': label + 1,
                            'picking_id': picking.id,
                            'lot_num': line.lot_id.name if life_date else False,
                            'code': move_line.product_id.cbss,
                            'rs_name': move_line.product_id.sanitary_reg_id.name,
                            'expiration': life_date.strftime('%b/%y').capitalize() if life_date else False,
                            'customer': picking.partner_id.parent_id.name or picking.partner_id.name,
                            'address': picking.partner_id.format_mx_address(),
                            'content': pack_qty,
                            'description': move_line.product_id.description_pickingout,
                            'labels_total': labels_count
                        })

                    if qty_rest > 0:
                        labels_ref.create({
                            'name': labels_count,
                            'picking_id': picking.id,
                            'lot_num': line.lot_id.name,
                            'code': move_line.product_id.cbss,
                            'rs_name': move_line.product_id.sanitary_reg_id.name,
                            'expiration': life_date.strftime('%b/%y').capitalize(),
                            'customer': picking.partner_id.parent_id.name or picking.partner_id.name,
                            'address': picking.partner_id.format_mx_address(),
                            'content': qty_rest,
                            'description': move_line.product_id.description_pickingout,
                            'labels_total': labels_count
                        })

    @api.multi
    def action_shipping_guide(self):

        wizard_id = self.env['sale.shipping.guide.wizard'].create({
            'picking_ids': [(6, 0, self.filtered(lambda r: r.delivery_date == False).ids)]
        })

        return {
            'name': 'Guía de embarque',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': wizard_id.id,
            'res_model': 'sale.shipping.guide.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': self.env.context
        }

    @api.multi
    def action_remove_shipping_guide(self):

        for picking_id in self.filtered(lambda r: r.delivery_date == False):

            picking_id.shipping_guide_id = False

    def locale_date_format(self, date_str, lformat, localef = 'es_MX.UTF-8'):
        """Parse date and format to specific locale"""

        locale.setlocale(locale.LC_TIME, localef)
        date_obj = parser.parse(date_str)

        return date_obj.strftime(lformat)


    def locale_date_format_vig(self, date_str, lformat, localef = 'es_MX.UTF-8'):
        """Parse date and format to specific locale in life_date"""    
        locale.setlocale(locale.LC_TIME, localef)
        date_obj = parser.parse(date_str)
        date_obj = date_obj - timedelta(hours=5)     
        return date_obj.strftime(lformat)


    def upper_index(self, s, upper_map = []):

        return "".join(c.upper() if i in upper_map else c for i, c in enumerate(s))



