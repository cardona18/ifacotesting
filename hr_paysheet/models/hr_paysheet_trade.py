# -*- coding: utf-8 -*-
# © <2016> <Omar Torres Silva (otorres@grupoifaco.com.mx) >
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models

class hr_paysheet_trade(models.Model):
    _name = 'hr.paysheet.trade'
    _description = 'Paysheet trade'

    _rec_name = 'concept_id'

    concept_id = fields.Many2one(
        string='Concepto',
        comodel_name='hr.paysheet.concept',
        ondelete='cascade',
        autojoin=True,
        index=True
    )
    code = fields.Integer(
        string='Codigo',
        related='concept_id.code',
        readonly=True,
        store=True,
        size=50
    )
    amount = fields.Float(
        string='Importe',
        digits=(18, 2)
    )
    paysheet_id = fields.Many2one(
        string='Nómina',
        comodel_name='hr.paysheet',
        ondelete='cascade',
        autojoin=True,
        index=True
    )
    year_id = fields.Many2one(
        string='Ejercicio',
        comodel_name='hr.paysheet.year',
        autojoin=True,
        index=True
    )

    _order = 'code ASC'