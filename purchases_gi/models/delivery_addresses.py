# -*- coding: utf-8 -*-
# © <2017> <Juan Carlos Vazquez Beas (jcvazquez@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models

class delivery_addresses(models.Model):
    """
    Se agregó el modelo Lugar de entrega ya que es necesario le catalogo en el módulo de compras.
    """
    _name = 'delivery.addresses'

    name = fields.Char(
        string='Lugar de entrega',
        required=True
    )
    addresses = fields.Text(
        string='Domicilio de entrega',
    )

