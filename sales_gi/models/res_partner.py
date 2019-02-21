# -*- coding: utf-8 -*-
# © <2016> <Omar Torres Silva (otorres@grupoifaco.com.mx) >
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api

class res_partner_gi(models.Model):
    _inherit = 'res.partner'

    lgsA226_ids = fields.Many2many(
        string='Grupos LgsA226',
        comodel_name='product.lgsa226'
    )
    expiration_months = fields.Integer(
        string='Caducidad (meses)',
        default=0,
        help="Mínimo de meses de caducidad que se le pueden surtir al cliente"
    )
    cfdi_mail = fields.Char(
        string='Correos CFDI',
        size=50
    )
    cfdi_mail_alt = fields.Text(
        string='Correos CFDI CC'
    )
    payment_method_id = fields.Many2one(
        string='Método de pago',
        comodel_name='l10n_mx_edi.payment.method'
    )
    sale_invoice_usage = fields.Selection(
        string='Usage',
        selection=[
            ('G01', 'Acquisition of merchandise'),
            ('G02', 'Returns, discounts or bonuses'),
            ('G03', 'General expenses'),
            ('I01', 'Constructions'),
            ('I02', 'Office furniture and equipment investment'),
            ('I03', 'Transportation equipment'),
            ('I04', 'Computer equipment and accessories'),
            ('I05', 'Dices, dies, molds, matrices and tooling'),
            ('I06', 'Telephone communications'),
            ('I07', 'Satellite communications'),
            ('I08', 'Other machinery and equipment'),
            ('D01', 'Medical, dental and hospital expenses.'),
            ('D02', 'Medical expenses for disability'),
            ('D03', 'Funeral expenses'),
            ('D04', 'Donations'),
            ('D05', 'Real interest effectively paid for mortgage loans (room house)'),
            ('D06', 'Voluntary contributions to SAR'),
            ('D07', 'Medical insurance premiums'),
            ('D08', 'Mandatory School Transportation Expenses'),
            ('D09', 'Deposits in savings accounts, premiums based on pension plans.'),
            ('D10', 'Payments for educational services (Colegiatura)'),
            ('P01', 'To define'),
        ],
        default='P01',
        help='Used in CFDI 3.3 to express the key to the usage that will '
        'gives the receiver to this invoice. This value is defined by the '
        'customer. \nNote: It is not cause for cancellation if the key set is '
        'not the usage that will give the receiver of the document.'
    )
    download_format = fields.Char(
        string='Formato descarga',
        help="""Nombre de archivo para descarga de facturas

# Variables disponibles
#----------------------
# rfc_emisor: RFC Emisor
# rfc_receptor: RFC Receptor
# folio_odoo: Folio de factura en odoo
# folio_siagi: Folio de factura en siagi
        """
    )

    def format_mx_address(self):

        return '%s%s%s%s%s%s%s%s%s' % (
            '%s ' % self.street_name if self.street_name else '',
            '%s ' % self.street_number if self.street_number else '',
            '%s ' % self.street_number2 if self.street_number2 else '',
            '%s ' % self.l10n_mx_edi_colony if self.l10n_mx_edi_colony else '',
            '%s ' % self.l10n_mx_edi_locality if self.l10n_mx_edi_locality else '',
            'CP: %s ' % self.zip if self.zip else '',
            '%s ' % self.city if self.city else '',
            '%s ' % self.state_id.name if self.state_id.name else '',
            self.country_id.name
        )