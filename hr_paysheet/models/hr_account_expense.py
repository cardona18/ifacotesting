# -*- coding: utf-8 -*-
# © <2016> <Omar Torres Silva (otorres@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models

class hr_account_expense(models.Model):
    _name = 'hr.account.expense'
    _description = 'HR ACCOUNT EXPENSE'

    name = fields.Char(
        string='Nombre',
        required=True
    )
    old_id = fields.Integer(
        string='Old id'
    )
    old_conf_ids = fields.One2many(
        string='Configuración',
        comodel_name='hr.segment.config',
        inverse_name='segment_id'
    )