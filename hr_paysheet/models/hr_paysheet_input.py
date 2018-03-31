# -*- coding: utf-8 -*-
# © <2016> <Omar Torres Silva (otorres@grupoifaco.com.mx) >
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from openerp import fields, models, api

_logger = logging.getLogger(__name__)

class hr_paysheet_input(models.Model):
    _name = 'hr.paysheet.input'
    _description = 'Paysheet input'

    _rec_name = 'code'

    code = fields.Char(
        string='Código',
        size=50
    )
    concept_id = fields.Many2one(
        string='Concepto',
        required=True,
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
    sys_input = fields.Boolean(
        string='Sistema',
        default=False
    )
    is_readonly = fields.Boolean(
        string='Solo lectura'
    )
    account1_id = fields.Many2one(
        string='Cuenta',
        comodel_name='hr.policy.line'
    )
    account2_id = fields.Many2one(
        string='Contra cuenta',
        comodel_name='hr.policy.line'
    )

    _order = 'code ASC'

    @api.onchange('concept_id')
    def check_change(self):
        self.code = self.generate_code()

    def generate_code(self):
        return ('I%s' % str(self.concept_id.code).zfill(3)) if self.concept_id.code else ''

    @api.model
    def create(self, vals):

        rec = super(hr_paysheet_input, self).create(vals)

        if not rec.code:

            rec.sudo().write({
                'code': rec.generate_code()
            })

        return rec