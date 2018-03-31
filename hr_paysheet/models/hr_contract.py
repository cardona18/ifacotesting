# -*- coding: utf-8 -*-
# © <2016> <Omar Torres Silva (otorres@grupoifaco.com.mx) >
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime, timedelta
from dateutil import tz
import calendar
import logging

from openerp import fields, models, api
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.exceptions import UserError
from openerp.tools.translate import _

from hr_paysheet import PaysheetTools

_logger = logging.getLogger(__name__)

class hr_contract_gi(models.Model):
    _inherit = 'hr.contract'

    # CONSTANTS
    SMDF = 75.49
    SDI_LIMIT = 25
    HOLIDAYS_PERCENT = 0.25
    YEAR_DAYS = 365
    XMAS_BONUS_CONCEPT = 24
    PANTRY_CODE = 15
    INT_FACTOR = 0.1
    HOLIDAYS_CONCEPT = 36
    PANTRY_FACTOR = 0.4
    MONTH_DAYS = 30.4166
    MAX_WB_PERCENT = 0.07
    WB_CODE = 38
    ANTIQUE_BONUS_CONCEPT = 81
    HOLIDAYS_SDI_TABLE = 'SDI_HOLIDAYS'
    WORKED_DAYS_FACTOR = 7.0 / 6.0
    WORKED_DAYS_CONCEPTS = [34]
    HOLIDAYS_CONCEPTS = [65, 36]
    BYMONTH_TABLE = [
        (1,2),
        (3,4),
        (5,6),
        (7,8),
        (9,10),
        (11,12)
    ]

    # FIELDS
    sdi = fields.Float(
        string='Salario base de cotización',
        digits=(16, 2)
    )
    sdi_real = fields.Float(
        string='Salario diario integrado',
        digits=(16, 2)
    )
    factor = fields.Float(
        string='Factor',
        readonly=True,
        digits=(16, 8),
        compute='_sdi_factor'
    )
    for_paysheet = fields.Boolean(
        string='Contrato de nómina',
        default=True
    )
    benefit_ids = fields.One2many(
        string='Prestaciones',
        comodel_name='hr.paysheet.benefit',
        inverse_name='contract_id'
    )
    salary_change_ids = fields.One2many(
        string='Cambios de salario',
        comodel_name='hr.salary.change',
        inverse_name='contract_id'
    )
    state = fields.Selection(
        string='Estado',
        size=10,
        selection=[
            ('draft', 'Borrador'),
            ('approved', 'Aprobado')
        ],
        default='draft'
    )
    active = fields.Boolean(
        string='Activo',
        default=True
    )
    company_id = fields.Many2one(
        string='Empresa',
        comodel_name='res.company'
    )

    def find_benefit(self, concept_id):

        """
            Find benefit and return it.
            @param concept_id: Find concept id.

            @return: Benefit object if its found, else False
        """

        self.ensure_one()

        if self.active:

            for benefit in self.benefit_ids:

                if (benefit.concept_id.code == concept_id) and (benefit.state == '1'):
                    return benefit

        else:

            for benefit in self.benefit_ids.search([('contract_id', '=', self.id), ('active', '=', False)]):

                if (benefit.concept_id.code == concept_id) and (benefit.state == '1'):
                    return benefit

        return False

    @api.multi
    def action_approve(self):

        self.state = 'approved'

    @api.onchange('employee_id')
    def check_change_employee_id(self):

        self.company_id = self.employee_id.company_id.id

    @api.multi
    def sdi_calc(self, period = False):
        """
        Calculate employee SDI.
        """

        current_date = datetime.today()
        last_year = current_date.year if period < 5 else current_date.year - 1

        if not period:

            period = -1

            for num, period_val in enumerate(self.BYMONTH_TABLE):

                if period_val[0] == current_date.month or period_val[1] == current_date.month:

                    if num == 0:
                        last_year -= 1
                        period_val = 5
                        continue

                    period = num - 1

        else:

            period -= 1

        year_id = self.env['hr.paysheet.year'].search([('name', '=', str(last_year))], limit=1)

        if not year_id.id:
            raise UserError('Ejercicio de nómina no encontrado: %s' % last_year)

        month1_id = self.env['hr.paysheet.month'].search([('year_id', '=', year_id.id), ('code', '=', str(self.BYMONTH_TABLE[period][0]))], limit=1)

        if not month1_id.id:
            raise UserError('Código de mes no encontrado: %s' % self.BYMONTH_TABLE[period][0])

        month2_id = self.env['hr.paysheet.month'].search([('year_id', '=', year_id.id), ('code', '=', str(self.BYMONTH_TABLE[period][1]))], limit=1)

        if not month2_id.id:
            raise UserError('Código de mes no encontrado: %s' % self.BYMONTH_TABLE[period][1])

        # MAX EMPLOYEE SDI
        max_sdi = self.SMDF * self.SDI_LIMIT

        # DAILY HOLIDAYS WAGE
        row = self.env['hr.rank.table'].find_value(self.HOLIDAYS_SDI_TABLE, int(self.employee_id.antique_years()))
        dh_amount = row.fixed_amount if row else 6
        dh_wage = (dh_amount * self.wage * self.HOLIDAYS_PERCENT) / self.YEAR_DAYS

        # DAILY XMAS BONUS WAGE
        xb_benefit = self.find_benefit(self.XMAS_BONUS_CONCEPT)
        xb_wage = ((xb_benefit.amount if xb_benefit else 0) * self.wage) / self.YEAR_DAYS

        # SDI BASE
        sdi_base = self.wage + dh_wage + xb_wage

        # DATE RANGE WORKED DAYS
        worked_days  = month1_id.concepts_amount(self.WORKED_DAYS_CONCEPTS, self.employee_id.id)
        worked_days += month1_id.concepts_amount(self.HOLIDAYS_CONCEPTS, self.employee_id.id) * self.WORKED_DAYS_FACTOR
        worked_days += month2_id.concepts_amount(self.WORKED_DAYS_CONCEPTS, self.employee_id.id)
        worked_days += month2_id.concepts_amount(self.HOLIDAYS_CONCEPTS, self.employee_id.id) * self.WORKED_DAYS_FACTOR

        # PANTRY INTEGRATION
        pantry_sum  = month1_id.concepts_amount([self.PANTRY_CODE], self.employee_id.id)
        pantry_sum += month2_id.concepts_amount([self.PANTRY_CODE], self.employee_id.id)
        pantry_lim  = max(0, pantry_sum - (self.SMDF * worked_days * self.PANTRY_FACTOR))

        # _logger.debug('PANTRY SUM: %s, PANTRY LIM: %s', pantry_sum, pantry_lim)

        # UNLIMITED INTEGRATION
        unl_concepts = self.env['hr.paysheet.concept'].search([
            ('sdi_integration', '=', 'UNL')
        ])
        unl_codes = [unl_concept.code for unl_concept in unl_concepts]
        unl_sum  = month1_id.concepts_amount(unl_codes, self.employee_id.id)
        unl_sum += month2_id.concepts_amount(unl_codes, self.employee_id.id)

        pre_sdi = min(max_sdi, sdi_base + ((pantry_lim + unl_sum) / worked_days if worked_days > 0 else 0))

        # _logger.debug('PRE SDI1: %s', pre_sdi)

        # LIMITED INTEGRATION
        lim_concepts = self.env['hr.paysheet.concept'].search([
            ('sdi_integration', '=', 'LIM')
        ])
        lim_codes = [lim_concept.code for lim_concept in lim_concepts]
        lim_sum  = month1_id.concepts_amount(lim_codes, self.employee_id.id)
        lim_sum += month2_id.concepts_amount(lim_codes, self.employee_id.id)
        lim_int = max(0, lim_sum - pre_sdi * worked_days * self.INT_FACTOR)

        pre_sdi += lim_int / worked_days if worked_days > 0 else 0

        # _logger.debug('PRE SDI2: %s', pre_sdi)

        sdi = min(max_sdi, pre_sdi)

        return {
            'pre_sdi': pre_sdi,
            'var_income': pantry_lim + unl_sum,
            'pantry_sum': pantry_sum,
            'natural_days': worked_days,
            'max_sdi': max_sdi,
            'dh_wage': dh_wage,
            'xb_wage': xb_wage,
            'sdi_base': sdi_base,
            'sdi': sdi
        }

    @api.one
    def _sdi_factor(self):
        """
        Calculate SDI factor.
        """

        if(self.sdi == 0 or self.wage == 0):
            return

        self.factor = self.sdi / self.wage


    def update_benefit(self, _table_id, _code, _date = datetime.today()):

        concept = self.env['hr.paysheet.concept'].search([('code', '=', _code)], limit=1)

        if not concept or not self.employee_id.in_date:
            return

        from_date = datetime.strptime(self.employee_id.in_date, DEFAULT_SERVER_DATE_FORMAT)
        to_date = datetime.strptime(_date, DEFAULT_SERVER_DATE_FORMAT) if type(_date) is str else _date
        to_date = to_date + timedelta(days=1)
        pstools = PaysheetTools()
        years = pstools.trunc_decimals((to_date - from_date).days / 365.25, 2)

        # _logger.debug("YEARS ROUND: %s, DAYS: %s, YEARS RAW: %s", years, (to_date - from_date).days, (to_date - from_date).days / 365.0)

        row = self.env['hr.rank.table'].find_value(_table_id, years)

        if not row:
            return

        benefit = self.benefit_ids.search([('contract_id', '=', self.id), ('concept_id', '=', concept.id)], limit=1)

        if not benefit:
            return

        benefit.amount = row.fixed_amount

    def change_timezone(self, _date, _time_zone = "America/Mexico_City"):

        # CONVER TO UTC
        _date = _date.replace(tzinfo = tz.gettz('UTC'))

        # LOAD TIMEZONE
        to_zone  = tz.gettz(_time_zone)

        return _date.astimezone(to_zone)

    @api.multi
    def action_update_benefits(self):
        """
        Update contract benefits called from button
        """

        self.update_benefits()


    @api.multi
    def update_benefits(self, _date = datetime.today()):

        if not self.employee_id.in_date:
            return

        from_date = datetime.strptime(self.employee_id.in_date, DEFAULT_SERVER_DATE_FORMAT)
        to_date = datetime.strptime(_date, DEFAULT_SERVER_DATE_FORMAT) if type(_date) is str else _date
        to_date = to_date + timedelta(days=1)
        pstools = PaysheetTools()
        years = pstools.trunc_decimals((to_date - from_date).days / 365.25, 2)


        for benefit in self.benefit_ids:

            if benefit.concept_id.code == self.WB_CODE:

                benefit.amount = round(self.MONTH_DAYS * self.sdi * self.MAX_WB_PERCENT)

                continue

            if not benefit.table_id.id:
                continue

            if benefit.concept_id.code == self.ANTIQUE_BONUS_CONCEPT:
                current_date = datetime.today()
                last_day = calendar.monthrange(current_date.year, current_date.month)[1]
                to_date = current_date.replace(day=last_day) + timedelta(days=1)
                years = pstools.trunc_decimals((to_date - from_date).days / 365.25, 2)

            # _logger.debug("CODE: %s, YEARS ROUND: %s, DAYS: %s, YEARS RAW: %s", benefit.concept_id.code, years, (to_date - from_date).days, (to_date - from_date).days / 365.25)

            row = benefit.table_id.self_find(years)

            if not row:
                continue

            benefit.amount = row.fixed_amount

    def set_sdi_real(self, sdi):
        self.sdi_real = sdi


class hr_contract_type_gi(models.Model):
    _inherit = 'hr.contract.type'

    code = fields.Char(
        string='Clave'
    )

    @api.multi
    def name_get(self):

        res = []

        for item in self:
            res.append((item.id, item.code + ' - ' + item.name if item.code and item.name else item.name))

        return res