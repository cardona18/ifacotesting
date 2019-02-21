# -*- coding: utf-8 -*-
# © <2017> <Juan Carlos Vazquez Beas (jcvazquez@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api
import logging

_logger = logging.getLogger(__name__)

class product_gi(models.Model):
    """
    Se heredó la clase productos para agregar productos y funciones.
    """
    _inherit = 'product.template'
    _description = 'Personalización del catalogo de productos GI'

    type_of_provenance = fields.Selection(
        [('national','Nacional'),
        ('import', 'Importación')], 
        string='Tipo de Procedencia', 
        default='national',
    )
    foreign_exchange = fields.Many2one(
        'res.currency',
        string='Moneda',
    )
    average_variation_pur = fields.Float(
        'Porcentaje de variación de compra',
    )
    maquila = fields.Boolean(
        string='Maquila',
    )

    inputs_for_manufacturing = fields.Boolean(
        string='Insumo para la fabricación',
    )

    import_license = fields.Many2one(
        string='Permiso de importación',
        comodel_name='import.licenses',
    )

