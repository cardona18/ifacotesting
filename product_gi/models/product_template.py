# -*- coding: utf-8 -*-
# © <2016> <Omar Torres Silva (otorres@grupoifaco.com.mx) >
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api
from odoo.exceptions import RedirectWarning

class product_template_gi(models.Model):
    _inherit = 'product.template'

    product_class = fields.Selection(
        string='Clase de producto',
        size=2,
        selection=[
            ('ME', 'Medicamento'),
            ('FA', 'Farmoquímico'),
            ('BI', 'Biotecnológico'),
            ('EN', 'Envase'),
            ('EA', 'Empaque y accesorios')
        ]
    )
    short_cbss = fields.Char(
        string='CBSS (Simple)',
        size=20
    )
    cbss = fields.Char(
        string='CBSS',
        size=20,
        help="Clave de cuadro básico completa"
    )
    concentration = fields.Char(
        string='Concentración'
    )
    presentation = fields.Char(
        string='Presentación'
    )
    sanitary_reg_id = fields.Many2one(
        string='Registro sanitario',
        comodel_name='product.sanitary.registration'
    )

    def _get_default_category_id(self):
        if self._context.get('categ_id') or self._context.get('default_categ_id'):
            return self._context.get('categ_id') or self._context.get('default_categ_id')
        category = self.env.ref('product.product_category_all', raise_if_not_found=False)
        if not category:
            category = self.env['product.category'].search([], limit=1)
        if category:
            return category.id
        else:
            err_msg = _('You must define at least one product category in order to be able to create products.')
            redir_msg = _('Go to Internal Categories')
            raise RedirectWarning(err_msg, self.env.ref('product.product_category_action_form').id, redir_msg)

    categ_id = fields.Many2one(
        'product.category', 'Internal Category',
        change_default=True, default=_get_default_category_id,
        track_visibility="onchange", required=True, help="Select category for the current product")

    @api.onchange('cbss')
    def check_change_cbss(self):

        try:
            self.short_cbss = str(self.cbss[5:9])
        except Exception as e:
            self.short_cbss = False

class product_product_gi(models.Model):
    _inherit = 'product.product'

    @api.onchange('cbss')
    def check_change_cbss(self):

        try:
            self.short_cbss = str(self.cbss[5:9])
        except Exception as e:
            self.short_cbss = False