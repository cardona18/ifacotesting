# -*- coding: utf-8 -*-
# © <2016> <Omar Torres Silva (otorres@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models

class hr_segment_config(models.Model):
    _name = 'hr.segment.config'
    _description = 'HR SEGMENT CONFIG'


    segment_id = fields.Many2one(
        string='Centro de costo',
        comodel_name='hr.account.expense',
        ondelete='cascade'
    )
    company_id = fields.Many2one(
        string='Empresa',
        comodel_name='res.company'
    )
    base_account = fields.Integer(
        string='Cuenta contable'
    )
