# -*- coding: utf-8 -*-
# © <2016> <Omar Torres Silva (otorres@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api

class hr_council_payment(models.Model):
    _name = 'hr.council.payment'
    _description = 'HR COUNCIL PAYMENT'

    CONCEPT_MAP = [
        ('3231', 'A CUENTA DE REMANENTE A DIST'),
        ('3442', 'COMPLEMENTO REMANENTE DIST'),
        ('3230', 'HONORARIOS DE CONSEJO'),
        ('3745', 'REMANENTE DISTRIBUIBLE')
    ]


    @api.multi
    def _state_tax(self):

        for payment in self:
            payment.state_tax = payment.amount * payment.member_id.state_tax if payment.member_id.state_tax else 0

    @api.multi
    def _tax_amount(self):

        for payment in self:
            payment.tax_amount = (payment.amount - payment.state_tax) * 0.35

    member_id = fields.Many2one(
        string='Persona',
        comodel_name='hr.council.member'
    )
    company_id = fields.Many2one(
        string='Empresa',
        comodel_name='res.company'
    )
    bank_id = fields.Many2one(
        string='Banco',
        comodel_name='res.bank'
    )
    bank_account = fields.Char(
        string='Cuenta bancaria',
        size=20,
        required=True
    )
    amount = fields.Float(
        string='Importe'
    )
    concept = fields.Selection(
        string='Concepto',
        selection=CONCEPT_MAP
    )
    state_tax = fields.Float(
        string='Impuesto estatal',
        compute=_state_tax
    )
    tax_amount = fields.Float(
        string='ISR',
        compute=_tax_amount
    )