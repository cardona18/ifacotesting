# -*- coding: utf-8 -*-
# © <2017> <Juan Carlos Vazquez Beas (jcvazquez@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models

class purchase_consignee(models.Model):
    """
    Se agregó el modelo consignatario ya que es necesario el catalogo en el módulo de compras.
    """
    _name = 'purchase.consignee'

    name = fields.Char(
        string='Consignatario',
        required=True
    )
    address = fields.Text(
        string='Domicilio',
        required=False,
        readonly=False,
    )