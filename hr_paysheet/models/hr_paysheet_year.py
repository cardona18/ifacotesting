# -*- coding: utf-8 -*-
# © <2016> <Omar Torres Silva (otorres@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime, timedelta
import calendar

from openerp import fields, models, api
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT

class hr_paysheet_year(models.Model):
    _name = 'hr.paysheet.year'
    _description = 'HR PAYSHEET YEAR'

    def last_day_of_week(self, year, dow):
        last_year_day = calendar.monthrange(year, 12)[1]
        last_year_date = datetime.today().replace(month=12, day=last_year_day, year=year)

        while(last_year_date.weekday() != dow):
            last_year_date -= timedelta(days=1)

        return last_year_date

    def _default_from_date(self):
        return self.last_day_of_week(datetime.today().year, 3)

    def _default_to_date(self):
        return self.last_day_of_week(datetime.today().year + 1, 2)

    name = fields.Char(
        string='Nombre',
        default=datetime.today().year + 1
    )
    from_date = fields.Date(
        string='Desde',
        default=_default_from_date
    )
    to_date = fields.Date(
        string='Hasta',
        default=_default_to_date
    )
    month_ids = fields.One2many(
        string='Periodos',
        comodel_name='hr.paysheet.month',
        inverse_name='year_id'
    )

    def get_days(self):

        fdate = datetime.strptime(self.from_date, DEFAULT_SERVER_DATE_FORMAT)
        tdate = datetime.strptime(self.to_date, DEFAULT_SERVER_DATE_FORMAT)

        return (tdate - fdate).days + 1

    YEAR_MONTHS = {
        1: 'ENERO',
        2: 'FEBRERO',
        3: 'MARZO',
        4: 'ABRIL',
        5: 'MAYO',
        6: 'JUNIO',
        7: 'JULIO',
        8: 'AGOSTO',
        9: 'SEPTIEMBRE',
        10: 'OCTUBRE',
        11: 'NOVIEMBRE',
        12: 'DICIEMBRE'
    }

    @api.multi
    def generate_periods(self):

        currrent_date = datetime.today().replace(year=int(self.name))

        for month in self.YEAR_MONTHS:

            max_days = calendar.monthrange(currrent_date.year, month)

            self.env['hr.paysheet.month'].create({
                'name': '%s/%s' % (self.YEAR_MONTHS[month], self.name),
                'code': month,
                'fdate': currrent_date.replace(day=1, month=month),
                'tdate': currrent_date.replace(day=max_days[1], month=month),
                'year_id': self.id
            })

    def concepts_amount(self, concepts, employee_id, lot_types = False):

        codes = ','.join(str(code) for code in concepts)

        query = """
            SELECT COALESCE(SUM(ABS(amount)), 0)
            FROM hr_paysheet_trade pt
            INNER JOIN hr_paysheet ps ON pt.paysheet_id = ps.id
            INNER JOIN hr_paysheet_lot psl ON ps.lot_id = psl.id
            INNER JOIN hr_paysheet_concept pc ON pt.concept_id = pc.id
            WHERE pt.year_id = %s
            AND ps.employee_id = %s
            AND pc.code IN (%s)
            %s
        """ % (
            self.id,
            employee_id,
            codes,
            '' if not lot_types else ' AND ltype IN (%s)' % lot_types
        )

        self.env.cr.execute(query)

        return self.env.cr.fetchone()[0]

    def fill_days(self, start_date, employee):
        """
        Calculate employee missing days in accountant year
        """

        fill_days = 0

        antique_date = datetime.strptime(employee.in_date, DEFAULT_SERVER_DATE_FORMAT)
        in_date = datetime.strptime(employee.reg_date, DEFAULT_SERVER_DATE_FORMAT)
        start_year_date = datetime.strptime(self.from_date, DEFAULT_SERVER_DATE_FORMAT)
        stop_year_date = datetime.strptime(self.to_date, DEFAULT_SERVER_DATE_FORMAT)
        last_period_date = datetime.strptime(start_date, DEFAULT_SERVER_DATE_FORMAT)

        if (start_year_date < in_date < stop_year_date) and (antique_date < start_year_date):
            fill_days += (in_date - start_year_date).days

        fill_days += (stop_year_date - last_period_date).days

        return fill_days