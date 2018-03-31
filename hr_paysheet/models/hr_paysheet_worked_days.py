# -*- coding: utf-8 -*-
# © <2016> <Omar Torres Silva (otorres@grupoifaco.com.mx) >
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models

class hr_paysheet_inputs(models.Model):
    _name = 'hr.paysheet.inputs'
    _description = 'Paysheet input'

    _rec_name = 'code'

    code = fields.Char(
        string='Código',
        related='concept_id.name'
        size=80
    )
    concept_id = fields.Many2one(
        string='Concepto',
        comodel_name='hr.paysheet.concept',
        ondelete='cascade'
    )
    amount = fields.Float(
        string='Cantidad',
        required=True,
        digits=(18,2)
    )
    paysheet_id = fields.Many2one(
        string='Nómina',
        comodel_name='hr.paysheet',
        ondelete='cascade'
    )