# -*- coding: utf-8 -*-
# © <2016> <Omar Torres Silva (otorres@grupoifaco.com.mx) >
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api

class hr_paysheet_benefit(models.Model):
    _name = 'hr.paysheet.benefit'
    _description = 'Paysheet benefit'

    _rec_name = 'concept_id'

    concept_id = fields.Many2one(
        string='Concepto',
        required=True,
        comodel_name='hr.paysheet.concept',
        domain="[('is_benefit','=',True)]",
        ondelete='cascade'
    )
    code = fields.Integer(
        string='Código',
        readonly=True,
        related='concept_id.code'
    )
    btype = fields.Selection(
        string='Tipo',
        required=True,
        selection=[
            ('DI', 'Días'),
            ('PO', 'Porcentaje'),
            ('CA', 'Cantidad')
        ]
    )
    amount = fields.Float(
        string='Cantidad',
        required=True,
        digits=(18,2)
    )
    table_id = fields.Many2one(
        string='Tabla',
        comodel_name='hr.rank.table'
    )
    contract_id = fields.Many2one(
        string='Contrato',
        comodel_name='hr.contract',
        ondelete='cascade'
    )
    state = fields.Selection(
        string='Estado',
        default='1',
        size=1,
        selection=[
            ('1', 'Activa'),
            ('0', 'Inactiva')
        ]
    )
    active = fields.Boolean(
        string='Activa',
        related='contract_id.active'
    )