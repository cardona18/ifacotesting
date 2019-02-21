# -*- coding: utf-8 -*-
# © <2016> <Omar Torres Silva (otorres@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models

class res_bank(models.Model):
    _inherit = 'res.bank'

    ledger_name = fields.Char(
        string='Razón social'
    )