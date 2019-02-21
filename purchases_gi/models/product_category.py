# -*- coding: utf-8 -*-
# © <2017> <Juan Carlos Vazquez Beas (jcvazquez@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models

class product_category(models.Model):
    """
    Se heredó la clase para agregar campos necesarios en las categorías de productos.
    """
    _inherit = 'product.category'
    _description = 'PRODUCT CATEGORY'

    operating_cost = fields.Integer(
        'Costo de operación',
    )
    manufacturing = fields.Integer(
        'Fabricación',
    )
    sales = fields.Integer(
        'Ventas',
    )
    admin = fields.Integer(
        'Administración',
    )
    investigation = fields.Integer(
        'Investigación ',
    )
    apportionment = fields.Boolean(
        string='Prorrateo',
    )
    description_cat = fields.Text(
        string='Requerimientos mínimos de compra',
    )
    user_requirements = fields.Boolean(
        string='Requiere formato "Requerimientos de usuario"',
    )