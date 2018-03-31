# -*- coding: utf-8 -*-
# © <2017> <Omar Torres Silva (otorresgi18@gmail.com)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from openerp import fields, models, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class hr_retention_wizard(models.TransientModel):
    _name = 'hr.retention.wizard'
    _description = 'HR RETENTION WIZARD'

    employee_id = fields.Many2one(
        string='Empleado',
        comodel_name='hr.employee'
    )
    credit_type = fields.Selection(
        string='Tipo de crédito',
        size=3,
        selection=[
            ('INF', 'Infonavit'),
            ('FON', 'Fonacot')
        ]
    )
    discount_type = fields.Selection(
        string='Tipo de descuento',
        size=1,
        selection=[
            ('1', 'Porcentaje'),
            ('2', 'Cuota Fija Monetaria'),
            ('3', 'Cuota Fija en VS')
        ]
    )
    vs_number = fields.Float(
        string='V.S.M',
        digits=(16, 4),
        default=0.0
    )
    vs_daily_amount = fields.Float(
        string='Retencion por día',
        digits=(16, 2),
        default=0.0
    )
    cf_fixed_amount = fields.Float(
        string='Cuota fija',
        digits=(16, 2),
        default=0.0
    )
    sdi_percent = fields.Float(
        string='Porcentaje',
        digits=(16, 2),
        default=0.0
    )
    credit_amount = fields.Float(
        string='Retención',
        digits=(16, 4),
        help="Retencion semanal del empleado por concepto de crédito infonavit"
    )
    diff_amount = fields.Float(
        string='Excedente anual',
        digits=(16, 4),
        help="Criterio de comprobación: N < 0"
    )
    fo_daily_income = fields.Float(
        string='Ingreso diario',
        digits=(16, 2)
    )
    fo_months_num = fields.Integer(
        string='Mensualidades'
    )
    fo_year_amount = fields.Float(
        string='Total a pagar',
        digits=(16, 2)
    )
    fo_year_discount = fields.Float(
        string='Descuento del periodo',
        digits=(16, 2)
    )
    fo_week_discount = fields.Float(
        string='Descuento semanal',
        digits=(16, 2)
    )
    fo_diff_amount = fields.Float(
        string='Diferencia',
        help="Criterio de comprobación: N < 0",
        digits=(16, 2)
    )

    @api.multi
    def action_calculate(self):

        DAYS_PER_WEEK = 7
        PERIOD_WEEKS  = 52
        PERIOD_MONTHS = 12
        MONTH_DAYS = 30.42
        MONTH_WEEKS = 4.0

        if self.credit_type == 'INF':

            if self.discount_type == '1':

                contract = self.env['hr.contract'].sudo().search([
                    ('employee_id', '=', self.employee_id.id),
                    ('for_paysheet', '=', True)
                ], limit=1)

                if not contract:
                    raise UserError("No se encotró el contrato del empleado")

                year_discount1 = (round((contract.sdi * (self.sdi_percent / 100.0)) + (15.0 / 2.0), 2) * MONTH_DAYS ) * PERIOD_MONTHS
                year_discount2 = self.vs_daily_amount * DAYS_PER_WEEK * PERIOD_WEEKS

                self.diff_amount = min(0, year_discount1 - year_discount2 )

            if self.discount_type == '2':

                year_discount1 = round(self.cf_fixed_amount + (15.0/2.0), 2) * PERIOD_MONTHS
                year_discount2 = self.vs_daily_amount * DAYS_PER_WEEK * PERIOD_WEEKS

                self.diff_amount = min(0, year_discount1 - year_discount2 )


            if self.discount_type == '3':

                rule = self.env['hr.paysheet.rule'].sudo().search([('code', '=', 'SM')], limit=1)

                if not rule:
                    raise UserError("No se encotró la configuración de salario mínimo")

                year_discount1 = round((rule.fixed_value * self.vs_number) + (15.0/2.0), 2) * PERIOD_MONTHS
                year_discount2 = self.vs_daily_amount * DAYS_PER_WEEK * PERIOD_WEEKS

                self.diff_amount = min(0, year_discount1 - year_discount2 )

            self.credit_amount = self.vs_daily_amount * DAYS_PER_WEEK

        if self.credit_type == 'FON':

            self.fo_week_discount = self.fo_daily_income * DAYS_PER_WEEK
            self.fo_year_discount = self.fo_week_discount * MONTH_WEEKS * self.fo_months_num
            self.fo_diff_amount = min(0, self.fo_year_amount - self.fo_year_discount)

        return {
            'type': 'ir.actions.report.xml_no_close'
        }