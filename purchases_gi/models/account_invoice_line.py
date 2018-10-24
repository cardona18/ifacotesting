
# -*- coding: utf-8 -*-
# © <2017> <Juan Carlos Vazquez Beas (jcvazquez@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import sys, logging
from openerp.osv import osv
from odoo import fields, models, api
from openerp.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class account_invoice_line(models.Model):
    """
    Se heredó la clase para adecuar la funcionalidad requerida y se agregaron campos y funciones. 
    """
    _inherit = 'account.invoice.line'

    def get_current_company_id(self):
        return self.env.user.company_id.id

    date_planned = fields.Date(
        string='Fecha planificada',
        required=False
    )

    product_id = fields.Many2one(
        string='Producto',
        comodel_name='product.product',
    )


    company_id = fields.Many2one(
        string='Empresa solicitante',
        comodel_name='res.company',
        default=get_current_company_id
    )

    account_id = fields.Many2one(
        string='Impuestos',
    )


    @api.onchange('account_id')
    def product_account_id(self):
        """
        Elimina la factura si el producto está vacío.
        """
        if not self.product_id:
            self.account_id = None


    @api.constrains('product_id')
    def _check_product_id(self):
        if not self.product_id and self.invoice_id.type == 'in_invoice':
            raise ValidationError('El producto es un campo obligatorio.')


    @api.constrains('account_analytic_id')
    def _check_account_analytic(self):
        if not self.account_analytic_id and self.invoice_id.type == 'in_invoice':
            raise ValidationError('La cuenta analitica es un campo obligatorio.')