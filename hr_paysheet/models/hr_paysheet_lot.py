# -*- coding: utf-8 -*-
# © <2016> <Omar Torres Silva (otorres@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime, timedelta
from dateutil import tz
from lxml import etree as ET
from M2Crypto import RSA
import base64
import calendar
import cStringIO
import hashlib
import json
import locale
import logging
import os
import re
import requests
import subprocess
import sys
import urllib
import urlparse
import uuid
import zipfile

from openerp import fields, models, api
from odoo.exceptions import UserError, Warning
from openerp.tools import config
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class hr_paysheet_lot(models.Model):
    _name = 'hr.paysheet.lot'
    _description = 'HR PAYSHEET LOT'

    _sql_constraints = [
        ('unique_lot', 'unique(company_id, ltype, old_id)', 'El lote que intenta crear ya existe.')
    ]

    name = fields.Char(
        string='Nombre',
        required=True
    )
    ltype = fields.Selection(
        string='Tipo',
        default='NO',
        required=True,
        size=2,
        selection=[
            ('NO', 'Normal'),
            ('ES', 'Especial'),
            ('PR', 'Prueba')
        ]
    )
    paycheck_text = fields.Char(
        string='Texto de recibo'
    )
    company_id = fields.Many2one(
        string='Compañia',
        comodel_name='res.company'
    )
    old_id = fields.Integer(
        string='Número'
    )
    struct_id = fields.Many2one(
        string='Estructura de nómina',
        comodel_name='hr.paysheet.struct',
        required=True
    )
    period_id = fields.Many2one(
        string='Periodo',
        comodel_name='hr.paysheet.month',
        required=True
    )
    from_date = fields.Date(
        string='Desde',
        required=True
    )
    to_date = fields.Date(
        string='Hasta',
        required=True
    )
    payment_date = fields.Date(
        string='Fecha de pago',
        required=True
    )
    paysheets_count = fields.Integer(
        string='Nóminas',
        compute='_paysheets_count',
    )
    paysheet_ids = fields.One2many(
        string='Nóminas',
        comodel_name='hr.paysheet',
        inverse_name='lot_id'
    )
    close_ids = fields.One2many(
        string='Cierre de concepto',
        comodel_name='hr.close.concept',
        inverse_name='lot_id'
    )
    policy_ids = fields.One2many(
        string='Póliza',
        comodel_name='hr.lot.policy',
        inverse_name='lot_id'
    )
    active = fields.Boolean(
        string='Activo',
        default=True
    )
    state = fields.Selection(
        string='Estado',
        default='draft',
        size=10,
        selection=[
            ('draft', 'Generado'),
            ('locked', 'Bloqueado'),
            ('signed', 'Timbrado'),
            ('closed', 'Cerrado')
        ]
    )

    def _paysheets_count(self):
        """
            Count all hr.paysheet related records
        """

        self.paysheets_count = self.paysheet_ids.search_count([('lot_id', '=', self.id)])

    @api.multi
    def calculate_lot(self):
        """
            Calculate each hr.paysheet related record
        """

        # CLEAN PAYSHEET MOVEMENTS

        self.env.cr.execute("""
            DELETE FROM hr_paysheet_trade WHERE id IN (
                SELECT pt.id
                FROM hr_paysheet_trade pt
                INNER JOIN hr_paysheet ps ON pt.paysheet_id = ps.id
                WHERE ps.lot_id = {0}
            )
        """.format(self.id))

        self.env.cr.commit()

        paysheets = self.paysheet_ids.search([('lot_id','=', self.id), ('state','in',('draft','error'))])

        count = 0
        total = len(paysheets)

        for paysheet in paysheets:

            if count % 10 == 0:
                _logger.debug("CALCULATED: %s OF: %s", count, total)

            paysheet.action_calculate()

            count += 1

    @api.multi
    def accumulate_lot(self):
        """
            Lock each hr.paysheet related record and lot
        """

        self.paysheet_ids.write({
            'state': 'locked'
        })

        self.state = 'locked'

    @api.multi
    def unlock_lot(self):
        """
            Unlock each hr.paysheet related record and lot
        """

        signed_paysheets = self.paysheet_ids.search_count([('lot_id', '=', self.id), ('state', '=', 'signed')])

        if signed_paysheets > 0:
            raise Warning('Ya se han timbrado nóminas, no se puede desbloquear el lote.')

        self.paysheet_ids.search([('lot_id', '=', self.id), ('state', '=', 'locked')]).write({
            'state': 'draft'
        })

        self.state = 'draft'

    @api.multi
    def sign_lot(self):
        """
            Calculate each hr.paysheet related record
        """

        # LOAD UTF-8 AS DEFAULT
        reload(sys)
        sys.setdefaultencoding('utf-8')

        sign_task = self.env['cfdi.sign.task'].sudo().create({
            'company_id': self.company_id.id
        })
        sign_task.prepare()

        paysheets = self.paysheet_ids.search([('lot_id', '=', self.id), ('state', 'in', ('locked','error'))])
        paysheets.action_sign({}, sign_task)

        error_count = self.paysheet_ids.search_count([('lot_id', '=', self.id), ('state', 'in', ('locked','error'))])

        if error_count == 0:
            self.state = 'signed'

    @api.multi
    def generate_txt_policy(self):
        """
            Generate TXT paysheet policy for each company
        """

        # SET DEAFULT ENCODING AS UTF-8
        reload(sys)
        sys.setdefaultencoding('utf-8')

        # RETRIEVE COMPANIES
        query  = """
            SELECT id, journal_id, name, old_id, short_name FROM res_company WHERE id IN (
            SELECT DISTINCT(rr.company_id) FROM hr_paysheet_trade pt
            INNER JOIN hr_paysheet ps ON pt.paysheet_id = ps.id
            INNER JOIN hr_employee he ON ps.employee_id = he.id
            INNER JOIN resource_resource rr ON he.resource_id = rr.id
            WHERE ps.lot_id = %s
            )
        """

        self.env.cr.execute(query % self.id)

        # INIT TMP DIRECTORY

        dir_id = str(uuid.uuid4()).replace('-','').upper()
        tmp_dir = "%s/tmp" % self.back_dir(os.path.realpath(__file__), 4)
        full_dir = "%s/%s" % (tmp_dir, dir_id)

        try:
            subprocess.check_output("mkdir -p {dir}/{id}".format(dir=tmp_dir,id=dir_id), shell=True, stderr=subprocess.STDOUT)
        except Exception, e:
            raise Warning('SYS001','%s' % e)

        try:
            zip_file = zipfile.ZipFile("%s.zip" % full_dir, "w")
        except Exception, e:
            raise Warning('ZIP001','%s' % e)

        for company in self.env.cr.fetchall():

            if not company[3]:
                continue

            # FIND PERIOD

            today = datetime.today()

            # RETRIEVE PERIODIC PAYMENT ACCOUNTS

            query = """
                SELECT ad.code, abs(sum(pt.amount))
                FROM hr_paysheet_trade pt
                INNER JOIN hr_paysheet ps ON pt.paysheet_id = ps.id
                INNER JOIN hr_employee he ON ps.employee_id = he.id
                INNER JOIN resource_resource rr ON he.resource_id = rr.id
                INNER JOIN hr_periodic_payment pp ON ps.employee_id = pp.employee_id
                INNER JOIN account_account ad ON pp.debtor_account = ad.id
                WHERE rr.company_id = {company_id}
                AND ps.lot_id = {lot_id}
                AND pp.concept_id = pt.concept_id
                GROUP BY ad.code
            """

            self.env.cr.execute(query.format(company_id=company[0], lot_id=self.id))

            pp_account_ids = self.env.cr.fetchall()

            # RETRIEVE ACCOUNT IDS
            query = """
                SELECT bs.code AS business_segment, ac.code AS cred_account, sum(pt.amount) AS balance
                FROM hr_paysheet_trade pt
                INNER JOIN hr_paysheet ps ON pt.paysheet_id = ps.id
                INNER JOIN hr_employee he ON ps.employee_id = he.id
                INNER JOIN hr_business_segment bs ON he.segment_id = bs.id
                INNER JOIN hr_paysheet_concept pc ON pt.concept_id = pc.id
                INNER JOIN hr_policy_config hpc ON hpc.concept_id = pc.id
                INNER JOIN hr_business_segment cc ON hpc.segment_id = cc.id
                INNER JOIN account_account ac ON hpc.creditor_account = ac.id
                WHERE hpc.company_id = {company_id} AND ps.lot_id = {lot_id}
                GROUP BY cc.name, business_segment, cred_account
                ORDER BY cc.name, business_segment, cred_account
            """

            self.env.cr.execute(query.format(company_id=company[0], lot_id=self.id))

            account_ids = self.env.cr.fetchall()

            if(not len(account_ids) and not len(pp_account_ids)):
                continue

            # Init txt file
            filename = 'PL_%s.txt' % str(uuid.uuid4()).replace('-','').upper()
            txt_file = open("%s/%s" % (full_dir, filename), "w")

            # write file header
            txt_file.write(('%spd500_201604' % company[4]).center(75,' ') + '\r\n')

            txt_file.write('P 20160414 3 00000500 1 000 Nómina Semanal   del %s al %s %s%s\r\n' % (
                self.locale_format_date(self.from_date, '%m/%b/%Y', 'es_MX.utf8', True),
                self.locale_format_date(self.to_date, '%m/%b/%Y', 'es_MX.utf8', True),
                ' ' * 71,
                '01 2'
            ))

            from_date = datetime.strptime(self.from_date, DEFAULT_SERVER_DATE_FORMAT)

            for account_id in pp_account_ids:

                txt_file.write('M {code}{desc} 2{amount}  0               0.00\r\n'.format(
                    code=str(account_id[0]).ljust(18),
                    amount=str(account_id[1]).rjust(17),
                    desc='NS%s' % from_date.strftime('%Y%m%d')
                ))


            for account_id in account_ids:

                txt_file.write('N %s \r\n' % account_id[0])

                txt_file.write('M {code}{desc} 1{amount}  0               0.00\r\n'.format(
                    code=str(account_id[1]).ljust(18),
                    amount=str(account_id[2]).rjust(17),
                    desc='NS%s' % from_date.strftime('%Y%m%d')
                ))

            txt_file.close()

            zip_file.write(txt_file.name, os.path.basename(txt_file.name), zipfile.ZIP_DEFLATED)

        try:
            subprocess.check_output("rm -rf {dir}/{id}".format(dir=tmp_dir,id=dir_id), shell=True, stderr=subprocess.STDOUT)
        except Exception, e:
            raise Warning('SYS002','%s' % e)

        self.delete_tmp_files()

        return {
            'type' : 'ir.actions.act_url',
            'url': '/web/binary/zip_file_download?path=%s' % urllib.quote_plus("%s.zip" % full_dir),
            'target': 'self',
        }

    @api.one
    def apply_policy(self):

        self.sudo().state = 'policy'

    @api.one
    def back_to_draft(self):

        self.sudo().state = 'draft'

    @api.one
    def back_to_locked(self):

        self.sudo().state = 'locked'

    def back_dir(self, _path, _positions):
        # Returns number of positions in path

        path_list = _path.strip('/').split('/')
        length = len(path_list)

        if(_positions >= length or _positions < 0):
                return ''

        for i in range(0, _positions):
                path_list.pop()

        return "/%s" % "/".join(path_list)

    def execute(self, _command):
        try:
            return subprocess.check_output(_command, shell=True, stderr=subprocess.STDOUT)
        except Exception, e:
            _logger.error('EXECUTE ERROR: %s', e)

    def locale_format_date(self, _date, _format, _locale, capital=False):
        # Convenrt date to locale format

        locale.setlocale(locale.LC_TIME, _locale)

        date = datetime.strptime(_date, DEFAULT_SERVER_DATE_FORMAT)

        res = date.strftime(_format)

        if(capital):
            s = list(res)
            s[3] = s[3].upper()
            res = "".join(s)

        return res

    @api.one
    def delete_tmp_files(self):

        tmp_path = "%s/tmp" % self.back_dir(os.path.realpath(__file__), 4)

        for filename in os.listdir(tmp_path):

            file = '%s/%s' % (tmp_path, filename)

            t = os.path.getmtime(file)

            fdate = self._utc_to_tz(datetime.fromtimestamp(t), "America/Mexico_City")
            cdate = self._utc_to_tz(datetime.now(), "America/Mexico_City")
            tdiff = (cdate - fdate).days

            if(tdiff >= 1):

                try:
                    subprocess.check_output("rm -rf {file}".format(file=file), shell=True, stderr=subprocess.STDOUT)
                except Exception, e:
                    _logger.error('DELETE ERROR: %s', e)

    def _utc_to_tz(self, _date, _time_zone):

        # CONVER TO UTC
        _date = _date.replace(tzinfo = tz.gettz('UTC'))

        # LOAD TIMEZONE
        to_zone  = tz.gettz(_time_zone)

        return _date.astimezone(to_zone)

    @api.multi
    def close_lot(self):

        EOM_DYAS = 5

        # SET SYSTEM TIMEZONE
        os.environ['TZ'] = "America/Mexico_City"

        # DELETE TMP MOVEMENTS
        self.env.cr.execute("""
            DELETE FROM hr_periodic_payment WHERE id IN (
                SELECT pp.id FROM hr_periodic_payment pp
                INNER JOIN hr_employee he ON pp.employee_id = he.id
                INNER JOIN resource_resource rr ON he.resource_id = rr.id
                WHERE rr.company_id = %s
                AND pp.mtype = 'ONE_DATE'
                AND pp.apply_date >= '%s'
                AND pp.apply_date <= '%s'
            )
        """ % (self.company_id.id, self.from_date, self.to_date))

        # ADD AMOUNT PAYMENTS HISTORY
        amount_payments = self.env['hr.periodic.payment'].search([
            ('company_id', '=', self.company_id.id),
            ('mtype', '=', 'AMOUNT'),
            ('paid', '=', False)
        ])

        for payment in amount_payments:

            self.env.cr.execute("""
                SELECT ABS(pt.amount) FROM hr_paysheet_trade pt
                INNER JOIN hr_paysheet ps ON pt.paysheet_id = ps.id
                WHERE pt.concept_id = %s AND ps.employee_id = %s AND ps.lot_id = %s
            """ % (payment.concept_id.id, payment.employee_id.id, self.id))

            amount = self.env.cr.fetchone()

            if not amount:
                continue

            payment.current_amount += amount[0]

            if payment.current_amount >= payment.amount_limit:
                payment.paid = True


        # ACCUMULATE YEAR
        for close in self.close_ids.search([('year_id', '=', self.period_id.year_id.id)]):

            next_year = close.year_id.search([('name', '=', datetime.today().year + 1)], limit=1)

            if not next_year:
                next_year = close.year_id.sudo().create({})

            self.env.cr.execute("""
                UPDATE hr_paysheet_trade SET year_id = %s WHERE id IN (
                    SELECT pt.id FROM hr_paysheet_trade pt
                    INNER JOIN hr_paysheet ps ON pt.paysheet_id = ps.id
                    WHERE ps.lot_id = %s AND pt.concept_id = %s
                )
            """ % (next_year.id, self.id, close.concept_id.id))

        self.env.cr.execute("""
            UPDATE hr_paysheet_trade SET year_id = %s WHERE id IN (
                SELECT pt.id FROM hr_paysheet_trade pt
                INNER JOIN hr_paysheet ps ON pt.paysheet_id = ps.id
                WHERE ps.lot_id = %s AND pt.year_id IS NULL
            )
        """ % (self.period_id.year_id.id, self.id))


        # CREATE NEXT PAYSHEET LOT
        fdate = datetime.strptime(self.from_date, DEFAULT_SERVER_DATE_FORMAT)
        tdate = datetime.strptime(self.to_date, DEFAULT_SERVER_DATE_FORMAT)
        acdate = datetime.strptime(self.payment_date, DEFAULT_SERVER_DATE_FORMAT)
        nacdate = acdate + timedelta(days=7)
        ntdate = tdate + timedelta(days=7)

        sequence = self.old_id + 1
        month_struct = self.env['hr.paysheet.struct'].search([('internal_type', '=', 'M')], limit=1)
        week_struct = self.env['hr.paysheet.struct'].search([('internal_type', '=', 'S')], limit=1)

        account_month = fdate.month if fdate.month == ntdate.month else ntdate.month
        account_year = fdate.year if fdate.year == ntdate.year else ntdate.year

        year = self.env['hr.paysheet.year'].search([
            ('name', '=', nacdate.year)
        ], limit=1)

        period = self.env['hr.paysheet.month'].search([
            ('year_id', '=', year.id),
            ('code', '=', nacdate.month)
        ], limit=1)

        if not year.id or not period.id:
            UserError('Error en periodo de nómina (%s, %s)' % (account_year, account_month))

        last_month_day = calendar.monthrange(account_year, account_month)[1]
        compare_date = ntdate.replace(
            day=last_month_day,
            month=account_month,
            year=account_year
        )

        diff_days = (compare_date.date() - ntdate.date()).days

        _logger.debug("COMPARE: %s, NEXT: %s, DIFF: %s", compare_date, ntdate, diff_days)

        self.create({
            'name': '%s/%s/%s' % (self.company_id.short_name, sequence, acdate.year),
            'old_id': sequence,
            'company_id': self.company_id.id,
            'from_date': fdate + timedelta(days=7),
            'to_date': ntdate,
            'struct_id': month_struct.id if diff_days <= EOM_DYAS else week_struct.id,
            'period_id': period.id,
            'payment_date': nacdate
        })

        # CLEAN SIGN ERROR DATA
        self.env.cr.execute("""
            UPDATE hr_paysheet SET last_error = NULL
            WHERE lot_id = %s
        """ % self.id)

        self.state = 'closed'
        self.active = False

    _order = 'payment_date'