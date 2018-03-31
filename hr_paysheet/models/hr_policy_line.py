# -*- coding: utf-8 -*-
# © <2017> <Omar Torres Silva (otorresgi18@gmail.com)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api

class hr_policy_line(models.Model):
    _name = 'hr.policy.line'
    _description = 'HR POLICY LINE'

    _sql_constraints = [
        ('unique_reg_hr_policy_line', 'unique(account,mtype,sign)', 'Ya se registró una linea igual')
    ]

    _rec_name = 'account'

    account = fields.Char(
        string='Cuenta',
        size=20,
        required=True
    )
    mtype = fields.Selection(
        string='Tipo',
        required=True,
        size=1,
        selection=[
            ('C', 'Cargo'),
            ('A', 'Abono')
        ]
    )
    sign = fields.Selection(
        string='Signo',
        required=True,
        size=1,
        selection=[
            ('+', 'Positivo'),
            ('-', 'Negativo')
        ]
    )

    @api.multi
    def name_get(self):

        res = []

        for item in self:
            res.append((item.id, '%s%s%s' % (item.account, item.mtype, item.sign)))

        return res