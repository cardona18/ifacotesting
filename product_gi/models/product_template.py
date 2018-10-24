# -*- coding: utf-8 -*-
# © <2016> <Omar Torres Silva (otorres@grupoifaco.com.mx) >
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api

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