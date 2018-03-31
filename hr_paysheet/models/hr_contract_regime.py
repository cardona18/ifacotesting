# -*- coding: utf-8 -*-
# © <2016> <Omar Torres Silva (otorres@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models

class hr_contract_regime(models.Model):
    _name = 'hr.contract.regime'
    _description = 'HR CONTRACT REGIME'

    name = fields.Char(
        string='Nombre',
        required=True
    )
    code = fields.Char(
        string='Clave',
        size=8
    )
