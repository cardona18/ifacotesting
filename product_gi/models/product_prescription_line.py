# -*- coding: utf-8 -*-
# © <2017> <Omar Torres Silva (otorres@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models

class product_prescription_line(models.Model):
    _name = 'product.prescription.line'
    _description = 'PRODUCT PRESCRIPTION LINE'

    registration_id = fields.Many2one(
        string='Registro sanitario',
        comodel_name='product.sanitary.registration'
    )
    product_id = fields.Many2one(
        string='Producto',
        comodel_name='product.product'
    )
    quantity = fields.Float(
        string='Cantidad',
        default=0.0,
        digits=(18, 6)
    )
    uom_id = fields.Many2one(
        string='Unidad de medida',
        comodel_name='product.uom'
    )