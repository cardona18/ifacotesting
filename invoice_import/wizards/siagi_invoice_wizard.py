# -*- coding: utf-8 -*-
# © <2017> <Omar Torres (otorresgi18@gmail.com)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
import subprocess
import json

from odoo import fields, models, api

_logger = logging.getLogger(__name__)

class siagi_invoice_wizard(models.TransientModel):
    _name = 'siagi.invoice.wizard'
    _description = 'SIAGI INVOICE WIZARD'

    company_id = fields.Many2one(
        string='Empresa',
        comodel_name='res.company',
        default=lambda self: self.env['res.company']._company_default_get('siagi.invoice.wizard')
    )
    rtype = fields.Selection(
        string='Redireccionar',
        default='F',
        size=1,
        selection=[
            ('F', 'Facturas'),
            ('N', 'Notas de crédito')
        ]
    )
    line_ids = fields.One2many(
        string='Facturas',
        comodel_name='siagi.invoice.line',
        inverse_name='wizard_id'
    )

    @api.multi
    def import_pending_invoices(self):

        pending_invoices = json.loads(self.execute('php /opt/php_files/invoice_query.php PEN %s' % self.company_id.invoice_db).decode('utf-8'))
        invoice_ref = self.env['account.invoice']

        for line_invoice in self.line_ids:

            exists = invoice_ref.search([
                ('company_id', '=', self.company_id.id),
                ('type', '=', 'out_invoice' if line_invoice.itype == 'F' else 'out_refund'),
                ('origin', '=', 'SIAGI/%s' % line_invoice.name)
            ])

            if exists.id:
                continue

            doc_index = '%s%s' % (line_invoice.itype, line_invoice.name)
            customer_id = self.env['res.partner'].search([('customer', '=', True), ('ref', '=', 'CLT%s' % pending_invoices[doc_index]['customer_ref'])])

            if not customer_id.id:
                _logger.debug("CLIENTE NO ENCONTRADO: %s %s", line_invoice.name, pending_invoices[doc_index]['customer_ref'])
                continue

            payment_term = False

            if line_invoice.itype == 'F':
                payment_term = self.env['account.payment.term.line'].sudo().search([('days', '=', pending_invoices[doc_index]['credit_days'])], limit=1)

            # SEARCH INVOICE DATA
            payment_method = self.env['l10n_mx_edi.payment.method'].sudo().search([('code', '=', pending_invoices[doc_index]['payment_method'])], limit=1)
            shipping_ids = self.env['res.partner'].sudo().search([('parent_id', '=', customer_id.id), ('type', '=', 'delivery')])
            shipping_id = customer_id.id
            position_id = False

            if len(shipping_ids) > 1:
                shipping_id = False

            if len(shipping_ids) == 1:
                shipping_id = shipping_ids.id

            if customer_id.sudo().property_account_position_id.id:

                position_id = self.env['account.fiscal.position'].sudo().search([
                    ('l10n_mx_edi_code', '=', customer_id.sudo().property_account_position_id.l10n_mx_edi_code),
                    '|',
                    ('company_id', '=', self.company_id.id),
                    ('company_id', '=', False)
                ], limit=1)


            invoice = invoice_ref.create({
                'origin': 'SIAGI/%s' % line_invoice.name,
                'company_id': self.company_id.id,
                'partner_id': customer_id.id,
                'date_invoice': pending_invoices[doc_index]['date'],
                'type': 'out_invoice' if line_invoice.itype == 'F' else 'out_refund',
                'l10n_mx_edi_payment_method_id': payment_method.id,
                'payment_term_id': payment_term.payment_id.id if payment_term else False,
                'partner_shipping_id': shipping_id,
                'fiscal_position_id': position_id.id if position_id else False,
                'l10n_mx_edi_usage': 'G01' if line_invoice.itype == 'F' else 'G02',
                'order_num': pending_invoices[doc_index]['so_num'] if line_invoice.itype == 'F' else False,
                'siagi_origin_inv': 'SIAGI/%s' % pending_invoices[doc_index]['refund_invoice'] if line_invoice.itype == 'N' else False
            })

            if line_invoice.itype == 'N':
                invoice.search_siagi_origin_inv()

            invoice_lines = eval(self.execute('php /opt/php_files/invoice_query.php %s %s %s' % (
                'DAT' if line_invoice.itype == 'F' else 'NCR',
                self.company_id.invoice_db,
                line_invoice.name
            )))

            for line in invoice_lines:

                product_uom_id = False
                line_tax = False

                if line_invoice.itype == 'F':

                    product = self.env['product.product'].search([('sale_ok', '=', True), ('default_code', '=', invoice_lines[line]['product_ref'])])

                    if not product.id:
                        _logger.debug("PRODUCT NOT FOUND: %s", invoice_lines[line]['product_ref'])
                        continue

                    product_uom = self.env['product.uom'].search([('name', '=', invoice_lines[line]['product_uom'].strip().replace('\\/','/'))], limit=1)
                    product_uom_id = product_uom.id

                    line_tax = self.env['account.tax'].search([
                        ('amount', '=', float(invoice_lines[line]['tax'])),
                        ('type_tax_use', '=', 'sale'),
                        '|',
                        ('company_id', '=', self.company_id.id),
                        ('company_id', '=', False)
                    ], limit=1)

                if line_invoice.itype == 'N':

                    product = self.env['product.product'].search([('sale_ok', '=', True), ('default_code', '=', 18461)])

                    if not product.id:
                        _logger.debug("NCR PRODUCT NOT FOUND: %s", 18461)
                        continue

                inv_line = self.env['account.invoice.line'].create({
                    'invoice_id': invoice.id,
                    'account_id': product.property_account_income_id.id or product.categ_id.property_account_income_categ_id.id if line_invoice.itype == 'F' else customer_id.property_account_payable_id.id,
                    'product_id': product.id,
                    'name': invoice_lines[line]['description'].replace('\\/','/'),
                    'quantity': invoice_lines[line]['qty'],
                    'price_unit': invoice_lines[line]['price'],
                    'import_line_annex': invoice_lines[line]['annex'] if line_invoice.itype == 'F' else False,
                    'invoice_line_tax_ids': [(6,0, [line_tax.id])] if line_tax else False,
                    'product_cbss': invoice_lines[line]['product_cbss'] if line_invoice.itype == 'F' else False,
                    'uom_id': product_uom_id if line_invoice.itype == 'F' else product.uom_id.id,
                    'product_uom_cfdi': invoice_lines[line]['product_uom'].replace('\\/','/') if line_invoice.itype == 'F' else False
                })

            invoice.compute_taxes()

            invoice.residual = invoice.amount_total

        if self.rtype == 'F':

            return {
                'name': 'Facturas de cliente',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'account.invoice',
                'views':  [(self.env.ref('account.invoice_tree').id, 'tree'), (self.env.ref('account.invoice_form').id, 'form')],
                'context': {'type':'out_invoice', 'journal_type': 'sale'},
                'domain': [('type', '=', 'out_invoice'), ('origin', 'like', 'SIAGI')],
                'type': 'ir.actions.act_window',
                'target': 'current',
            }

        else:

            return {
                'name': 'Notas de crédito',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'account.invoice',
                'views':  [(self.env.ref('account.invoice_tree').id, 'tree'), (self.env.ref('account.invoice_form').id, 'form')],
                'context': {'default_type': 'out_refund', 'type':'out_refund', 'journal_type': 'sale'},
                'domain': [('type', '=', 'out_refund'), ('origin', 'like', 'SIAGI')],
                'type': 'ir.actions.act_window',
                'target': 'current'
            }

    def execute(self, _command):
        try:
            return subprocess.check_output(_command, shell=True, stderr=subprocess.STDOUT)
        except Exception as e:
            _logger.error('EXECUTE ERROR: %s', e)


    @api.multi
    def create_import_wizard(self):

        wizard_id = self.create({})

        pending_invoices  = json.loads(self.execute('php /opt/php_files/invoice_query.php PEN %s' % wizard_id.company_id.invoice_db).decode('utf-8'))
        invoice_ref = self.env['account.invoice']

        self.env['siagi.invoice.line'].search([]).unlink()

        for docid in pending_invoices:

            dtype = docid[:1]
            code = docid[1:]

            exists = invoice_ref.search([
                ('company_id', '=', wizard_id.company_id.id),
                ('origin', '=', 'SIAGI/%s' % code)
            ])

            if exists.id:
                continue

            self.env['siagi.invoice.line'].create({
                'wizard_id': wizard_id.id,
                'name': code,
                'itype': dtype,
                'invoice_date': pending_invoices[docid]['date']
            })

        return {
            'name': 'Importar',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'siagi.invoice.wizard',
            'res_id': wizard_id.id,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': self.env.context
        }