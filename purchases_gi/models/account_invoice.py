# -*- coding: utf-8 -*-
# © <2017> <Juan Carlos Vazquez Beas (jcvazquez@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import sys, logging
from odoo import fields, models, api
from openerp.osv import osv

_logger = logging.getLogger(__name__)


class account_invoice(models.Model):
    """
    Se heredó la clase para adecuar la funcionalidad requerida.
    """
    _inherit = 'account.invoice'
    _sql_constraints = []


    # def get_config(self):
    #     date_planneds = []
    #     for id_line in self.invoice_line_ids:
    #         date_planneds.append(id_line.date_planned)

    #     date_planneds = list(set(date_planneds))

    #     if len(date_planneds) > 1:
    #         self.different_dates = True
    #     else:
    #         self.different_dates = False


    @api.multi
    def separate_invoices(self):
        """
            Crea una nueva factura relacionada y llama a la función button_reset_taxes del módulo de inventarios.
        """

        date_planneds = []
        for id_line in self.invoice_line_ids:
            date_planneds.append(id_line.date_planned)

        date_planneds = list(set(date_planneds))


        line_create = []
        for date_planned_id in date_planneds:
            id_line = self.env['account.invoice.line'].sudo().search([('invoice_id', '=', self.id),('date_planned','=',date_planned_id)])
            data_pla = {'date' : date_planned_id, 'id_line' : id_line}
            line_create.append(data_pla)
      


        cont = 0
        for line_create_id in line_create:
            if cont != 0:
                account_invoice_id = self.sudo().env['account.invoice'].create({
                    'partner_id': self.partner_id.id,
                    'origin': self.origin,
                    'order_id': self.order_id.id,
                    'account_id': self.account_id.id,
                    'journal_id': self.journal_id.id,
                    'currency_id': self.currency_id.id,
                    'user_id': self.user_id.id,
                    'company_id': self.company_id.id,
                })
                account_invoice_id.button_reset_taxes()

                self.order_id.sudo().write({'invoice_ids': [(4, [account_invoice_id.id])]})

                for line_id in line_create_id['id_line']:
                    line_id.invoice_id = account_invoice_id.id

                    _logger.warning(line_id.invoice_id.id)

            cont = cont + 1

        self.button_reset_taxes()


    def get_info_purchase_ord(self):
        """
            Obtiene el contexto de la orden de compra.
        """
        try:
            if self._context['journal_type'] == 'purchase':
                return True
        except KeyError:
            pass

    purchase_ok = fields.Boolean(
        string='Orden de compra',
        default=get_info_purchase_ord
    )


    order_id  = fields.Many2one(
        'purchase.order',
        string='Orden de compra relacionada',
    )


    # different_dates = fields.Boolean(
    #     string='¿Fechas diferentes?',
    #     required=False,
    #     compute=get_config
    # )
    folio = fields.Char(
        string='Folio del proveedor',
    )

    doc_xml = fields.Many2one(
        'data.filemanager',
        string='Xml',
    )

    @api.onchange('order_id')
    def onchange_order_id(self):
        """
            Verifica la cuenta analítica.
        """
        account_invoice_line_ids = []
        if self.order_id:
            for order_line_id in self.order_id.order_line:
                if not order_line_id.product_id.property_account_expense:
                    raise osv.except_osv('Advertencia','La cuenta analítica no esta definida en la orden de compra.')

                account_invoice_line_ids.append((0, 0, { 'product_id': order_line_id.product_id.id, 'account_id': order_line_id.product_id.property_account_expense.id, 'date_planned': order_line_id.date_planned, 'name': order_line_id.product_id.name, 'quantity': order_line_id.product_qty,'price_unit': order_line_id.price_unit_no_discount,'invoice_line_tax_id': order_line_id.taxes_id or False}))
            self.sudo().invoice_line = account_invoice_line_ids


    @api.onchange('invoice_line')
    def onchange_invoice_line(self):
        """
        Obtiene la cuenta analítica.
        """
        if self.invoice_line_ids:
            for invoice_line_id in self.invoice_line_ids:
                if invoice_line_id.product_id:
                    if invoice_line_id.account_id:
                        if self.account_id.company_id != self.company_id:
                            self.sudo().account_id = None
                        if not invoice_line_id.product_id.property_account_expense:
                            invoice_line_id.product_id.property_account_expense = None
                            invoice_line_id.sudo().product_id = None                        
                        else:
                           self.account_id  = invoice_line_id.product_id.property_account_expense.id


    @api.multi
    def write(self,vals):
        """
        Verifica la cuenta Costo de Venta.
        """
        res = super(account_invoice, self).write(vals)
        try:
            if vals['invoice_line']:
                for account_invoice_id in vals['invoice_line']:
                    _logger.warning("lineas de compra")
                    _logger.warning(account_invoice_id)
                    if account_invoice_id:
                        line_id = self.env['account.invoice.line'].sudo().search([('id', '=', account_invoice_id[1])])

                        if line_id.product_id:
                            if line_id.account_id:
                                if line_id.account_id.company_id != line_id.company_id:
                                    raise osv.except_osv('Advertencia','La "Cuenta costo de venta" asociada al producto pertenece a otra empresa.')

                                if not line_id.product_id.property_account_expense:
                                    raise osv.except_osv('Advertencia','Se debe configurar la "Cuenta Costo de Venta" en el producto.')
                                else:
                                    _logger.warning("Si modifica la cuenta :)")
                                    line_id.account_id  = line_id.product_id.property_account_expense.id
        except KeyError:
            pass

        return res



    def _prepare_invoice_line_from_po_line(self, line):
        """
        Sobreescribo metodo para obtener descuento desde la solicitud de cotizacion
        :param line:
        :return:
        """
        vals = super(account_invoice, self)._prepare_invoice_line_from_po_line(
            line)
        vals['discount'] = line.discount
        return vals

    reception_id = fields.Many2many(comodel_name="purchase.reception", string="Entrada asociada")
    with_receptions = fields.Char(string="Entradas relacionadas", default='Sin entradas')

    @api.onchange('invoice_line_ids')
    def _onchange_origin(self):
        purchase_ids = self.invoice_line_ids.mapped('purchase_id')
        if purchase_ids:
            self.origin = ', '.join(purchase_ids.mapped('name'))
            #self.reference = ', '.join(purchase_ids.filtered('partner_ref').mapped('partner_ref')) or self.reference