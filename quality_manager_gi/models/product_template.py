# -*- coding: utf-8 -*-
# © <2016> <Juan Carlos Vazquez Beas (jcvazquez@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api

class product_template(models.Model):
    _inherit = 'product.template'

    type_expiration = fields.Selection(
        string='Tipo de vigencia',
        size=3,
        selection=[
            ('cad', 'Caducidad'),
            ('rea', 'Reanalisis'),
        ]
    )
    is_checked = fields.Selection(
        [
            ('psychotropic','Psicotrópico'),
            ('narcotic', 'Estupefaciente'),
            ('antibiotic', 'Antibiótico'),
        ], 
        string='Controlado', 
    )