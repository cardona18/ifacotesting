# -*- coding: utf-8 -*-
# © <2016> <Omar Torres Silva (otorres@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models

class hr_policy_config(models.Model):
    _name = 'hr.policy.config'
    _description = 'HR POLICY CONFIG'

    company_id = fields.Many2one(
        string='Empresa',
        comodel_name='res.company'
    )
    segment_id = fields.Many2one(
        string='Centro de costo',
        comodel_name='hr.business.segment'
    )
    debtor_account = fields.Many2one(
        string='Cuenta 1',
        comodel_name='account.account',
    )
    type1 = fields.Selection(
        string='Tipo 1',
        size=1,
        selection=[
            ('C', 'Cargo'),
            ('A', 'Abono')
        ]
    )
    sign1 = fields.Selection(
        string='Signo 1',
        size=1,
        selection=[
            ('+', 'Positivo'),
            ('-', 'Negativo')
        ]
    )
    creditor_account = fields.Many2one(
        string='Cuenta 2',
        comodel_name='account.account',
        domain="[('company_id','=','company_id')]"
    )
    type2 = fields.Selection(
        string='Tipo 2',
        size=1,
        selection=[
            ('C', 'Cargo'),
            ('A', 'Abono')
        ]
    )
    sign2 = fields.Selection(
        string='Signo 2',
        size=1,
        selection=[
            ('+', 'Positivo'),
            ('-', 'Negativo')
        ]
    )
    concept_id = fields.Many2one(
        string='Concepto',
        comodel_name='hr.paysheet.concept'
    )
