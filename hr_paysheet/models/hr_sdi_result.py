# -*- coding: utf-8 -*-
# © <2016> <Omar Torres Silva (otorres@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models

class hr_sdi_result(models.TransientModel):
    _name = 'hr.sdi.result'
    _description = 'HR SDI RESULT'

    contract_id = fields.Many2one(
        string='Contrato',
        comodel_name='hr.contract'
    )
    wizard_id = fields.Many2one(
        string='Wizard',
        comodel_name='hr.sdi.calc'
    )
    sdi = fields.Float(
        string='SDI'
    )
    days = fields.Integer(
        string='Días'
    )
    pantry = fields.Float(
        string='Despensa'
    )
    xmas_bonus = fields.Float(
        string='Aguinaldo'
    )
    holidays = fields.Float(
        string='Vacaciones'
    )
    var_income = fields.Float(
        string='IV'
    )