# -*- coding: utf-8 -*-
# © <2016> <Omar Torres Silva (otorres@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api

class cfdi_financial_regime(models.Model):
    _name = 'cfdi.financial.regime'
    _description = 'CFDI FINANCIAL REGIME'

    name = fields.Char(
        string='Clave'
    )
    description = fields.Char(
        string='Nombre'
    )
    phy_person = fields.Boolean(
        string='Persona Física',
        help='Aplica para Persona Física'
    )
    moral_person = fields.Boolean(
        string='Persona Moral',
        help='Aplica para Persona Moral'
    )

    @api.multi
    def name_get(self):

        res = []

        for item in self:
            res.append((item.id, item.name + ' - ' + item.description))

        return res