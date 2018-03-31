# -*- coding: utf-8 -*-
# © <2016> <Omar Torres Silva (otorres@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models

class res_company_paysheet(models.Model):
    _inherit = 'res.company'

    old_id = fields.Integer(
        string='ID Empresa',
        required=True
    )
    old_db_name = fields.Char(
        string='DB Contable'
    )
    old_db = fields.Char(
        string='DB Nóminas'
    )
    payment_account_id = fields.Many2one(
        string='Cuenta de nómina',
        comodel_name='res.partner.bank',
        help='Cuenta bancaria para pagar la nómina a los empleados'
    )
    bank_account_id = fields.Many2one(
        string='Cuenta de pagos en banco',
        comodel_name='account.account',
        help='Cuenta contable para registrar pagos a empleados con deposito en banco'
    )
    bank_flow = fields.Char(
        string='Flujo (banco)',
        size=10
    )
    cash_account_id = fields.Many2one(
        string='Cuenta de pagos en efectivo',
        comodel_name='account.account',
        help='Cuenta contable para registrar pagos a empleados en efectivo'
    )
    cash_flow = fields.Char(
        string='Flujo (efectivo)',
        size=10
    )
    has_ptu = fields.Boolean(
        string='Genera utilidades',
        default=False
    )