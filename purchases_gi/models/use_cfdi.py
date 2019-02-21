# -*- coding: utf-8 -*-
# © <2018> < ()>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api

class use_cfdi(models.Model):
    """
    Se creó el catálogo por qué se necesita en el módulo de compras especificar el uso de CFDI
    """
    _name = 'use.cfdi'

    name = fields.Text(
        string='Descripción',
    )
    use_cfdi = fields.Char(
        string='Uso de CFDI',
        required=True
    )
