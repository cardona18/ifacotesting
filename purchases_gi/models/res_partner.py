# -*- coding: utf-8 -*-
# © <2017> <Juan Carlos Vazquez Beas (jcvazquez@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import sys, logging
from odoo import fields, models, api

_logger = logging.getLogger(__name__)

class res_partner(models.Model):
    """
    Hereda el modelo de para agregar campos al proveedor.
    """
    _inherit = 'res.partner'
    

    type_of_consumption = fields.Selection(
        [('service','Servicio'),
        ('product', 'Producto')], 
        string='Tipo de bien', 
        default='service',
    )

    description_consumption = fields.Text(
        string='Descripción del bien',
    )

    id_diot = fields.Char(
        string='ID Fiscal (DIOT)',
    )

    provider_for_manufacturing = fields.Boolean(
        string='Provee insumo para la fabricación',
    )

    origin = fields.Selection(
        [('national','Nacional'),
        ('foreign', 'Extranjero'), 
        ('group', 'Grupo')], 
        string='Origen', 
        default='national',
    )

    supplier_ledger_name = fields.Char(
        string='Razón social'
    )

    product_category = fields.Many2one(
        string='Categoría de productos',
        comodel_name='product.category',
    )
