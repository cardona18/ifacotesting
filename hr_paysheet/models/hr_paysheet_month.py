# -*- coding: utf-8 -*-
# © <2017> <Omar Torres Silva (otorresgi18@gmail.com)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime
import logging
import os

from openerp import fields, models
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT

_logger = logging.getLogger(__name__)

class hr_paysheet_month(models.Model):
    _name = 'hr.paysheet.month'
    _description = 'HR PAYSHEET MONTH'

    _sql_constraints = [
        ('unique_year_month', 'unique(year_id, code)', 'El periodo ya existe para este ejercicio.')
    ]

    name = fields.Char(
        string='Nombre'
    )
    code = fields.Integer(
        string='Clave',
        default=0
    )
    fdate = fields.Date(
        string='Desde'
    )
    tdate = fields.Date(
        string='Hasta'
    )
    year_id = fields.Many2one(
        string='Ejercicio',
        comodel_name='hr.paysheet.year',
        ondelete='cascade'
    )

    def month_lots(self, company_id = False, lot_types = False, states = False):

        self.env.cr.execute("""
            SELECT count(*)
            FROM hr_paysheet_lot psl
            WHERE company_id = %s
            AND period_id = %s
            %s %s
        """ % (
            company_id,
            self.id,
            ' AND psl.ltype %s' % lot_types if lot_types else '',
            ' AND psl.state %s' % states if states else ''
        ))

        return self.env.cr.fetchone()[0]

    def month_paysheets(self, employee_id = False, lot_types = False, states = False):

        self.env.cr.execute("""
            SELECT count(ps.id)
            FROM hr_paysheet ps
            INNER JOIN hr_paysheet_lot psl ON ps.lot_id = psl.id
            WHERE ps.employee_id = %s
            AND period_id = %s
            %s %s
        """ % (
            employee_id,
            self.id,
            ' AND psl.ltype %s' % lot_types if lot_types else '',
            ' AND psl.state %s' % states if states else ''
        ))

        return self.env.cr.fetchone()[0]

    def concepts_amount(self, concepts, employee_id, lot_types = False, states = False):

        codes = ','.join(str(code) for code in concepts)

        self.env.cr.execute("""
            SELECT COALESCE(SUM(ABS(amount)), 0)
            FROM hr_paysheet_trade pt
            INNER JOIN hr_paysheet ps ON pt.paysheet_id = ps.id
            INNER JOIN hr_paysheet_lot psl ON ps.lot_id = psl.id
            INNER JOIN hr_paysheet_concept pc ON pt.concept_id = pc.id
            WHERE psl.period_id = %s
            AND ps.employee_id = %s
            AND pc.code IN (%s) %s %s
        """ % (
            self.id,
            employee_id,
            codes,
            '' if not states else ' AND psl.state %s' % states,
            '' if not lot_types else ' AND psl.ltype %s' % lot_types
        ))

        return self.env.cr.fetchone()[0]

    def from_date(self, _date = False):

        # SET SYSTEM TIMEZONE
        os.environ['TZ'] = "America/Mexico_City"

        date = datetime.strptime(_date, DEFAULT_SERVER_DATE_FORMAT) if _date else datetime.today().date()

        year = self.env['hr.paysheet.year'].search([('name', '=', date.year)], limit=1)

        return self.search([('year_id', '=', year.id), ('code', '=', date.month)], limit=1)