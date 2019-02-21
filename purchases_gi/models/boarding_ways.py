# -*- coding: utf-8 -*-
# © <2017> <Juan Carlos Vazquez Beas (jcvazquez@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models

class boarding_ways(models.Model):
    """
    Se agregó el modelo Vías de embarque ya que es necesario le catalogo en el módulo de compras.
    """
    _name = 'boarding.ways'
    _description = 'Vías de embarque'

    name = fields.Char(
        string='Concepto',
        required=True
    )
    description = fields.Char(
        string='Abreviatura',
        required=False,
    )
