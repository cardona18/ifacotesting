# -*- coding: utf-8 -*-
# © <2016> <Omar Torres Silva (otorres@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api

class hr_lot_policy(models.Model):
    _name = 'hr.lot.policy'
    _description = 'HR LOT POLICY'

    name = fields.Char(
        string='Descripción'
    )
    lot_id = fields.Many2one(
        string='Lote',
        comodel_name='hr.paysheet.lot',
        ondelete='cascade'
    )
    account = fields.Char(
        string='Cuenta'
    )
    segment_code = fields.Char(
        string='Código de segmento'
    )
    debit_amount = fields.Float(
        string='Cargos'
    )
    credit_amount = fields.Float(
        string='Abonos'
    )
    cash_flow = fields.Char(
        string='Flujo de efectivo'
    )