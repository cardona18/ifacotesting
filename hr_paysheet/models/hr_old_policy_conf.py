# -*- coding: utf-8 -*-
# © <2016> <Omar Torres Silva (otorres@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models

class hr_old_policy_conf(models.Model):
    _name = 'hr.old.policy.conf'
    _description = 'HR OLD POLICY CONF'

    concept_id = fields.Many2one(
        string='Concepto',
        comodel_name='hr.paysheet.concept'
    )
    company_id = fields.Many2one(
        string='Empresa',
        comodel_name='res.company'
    )
    account1 = fields.Integer(
        string='Cuenta 1'
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
    account2 = fields.Integer(
        string='Cuenta 2'
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