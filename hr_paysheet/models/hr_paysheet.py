# -*- coding: utf-8 -*-
# © <2016> <Omar Torres Silva (otorres@grupoifaco.com.mx) >
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime
from dateutil import tz
from lxml import etree as ET
from M2Crypto import RSA
from urllib2 import URLError
import base64
import calendar
import hashlib
import json
import locale
import logging
import os
import random
import re
import requests
import subprocess
import sys
import urlparse
import uuid

from openerp import fields, models, api
from odoo.exceptions import UserError
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.tools.safe_eval import safe_eval as eval
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class hr_paysheet(models.Model):
    _name = 'hr.paysheet'
    _description = 'Paysheet'

    @api.multi
    def _calc_total(self):

        for item in self:
            item.total = item.perceptions - item.deductions

    name = fields.Char(
        string='Nombre',
        size=64
    )
    employee_id = fields.Many2one(
        string='Empleado',
        required=True,
        comodel_name='hr.employee'
    )
    contract_id = fields.Many2one(
        string='Contrato',
        required=True,
        comodel_name='hr.contract',
        domain="[('employee_id','=',employee_id)]"
    )
    payment_date = fields.Date(
        string='Fecha de pago'
    )
    lot_id = fields.Many2one(
        string='Lote de nómina',
        comodel_name='hr.paysheet.lot',
        ondelete='cascade'
    )
    inputs_ids = fields.One2many(
        string='Entradas',
        required=True,
        comodel_name='hr.paysheet.input',
        inverse_name='paysheet_id',
        auto_join=True
    )
    ignore_ids = fields.Many2many(
        string='Descartar',
        comodel_name='hr.paysheet.concept'
    )
    trade_ids = fields.One2many(
        string='Movimientos',
        comodel_name='hr.paysheet.trade',
        inverse_name='paysheet_id',
        auto_join=True
    )
    cfdi_ids = fields.One2many(
        string='Timbres',
        comodel_name='hr.xml.cfdi',
        inverse_name='paysheet_id'
    )
    last_error = fields.Text(
        string='Último error'
    )
    last_paysheet = fields.Boolean(
        string='Finiquito',
        default=False
    )
    struct_id = fields.Many2one(
        string='Estructura',
        comodel_name='hr.paysheet.struct'
    )
    leave_date = fields.Date(
        string='Fecha de salida'
    )
    ant_bonus_days = fields.Float(
        string='Días PA',
        help='Días prima de antigüedad'
    )
    leave_reward = fields.Boolean(
        string='Gratificación'
    )
    leave_reward_days = fields.Float(
        string='Días de gratificación'
    )
    reward_days = fields.Boolean(
        string='Indemnización (Días)'
    )
    reward_days_amount = fields.Float(
        string='Días de indemnización por año'
    )
    reward_months = fields.Boolean(
        string='Indemnización (Meses)'
    )
    reward_months_amount = fields.Float(
        string='Días de indemnización'
    )
    pending_holidays = fields.Integer(
        string='Vacaciones pendientes',
        default=0
    )
    perceptions = fields.Float(
        string='Percepciones'
    )
    deductions = fields.Float(
        string='Deducciones'
    )
    total = fields.Float(
        string='Total',
        compute=_calc_total
    )
    send_cfdi = fields.Boolean(
        string='Enviar CFDI',
        default=False
    )
    state = fields.Selection(
        string='Estado',
        default='draft',
        selection=[
            ('draft', 'Generada'),
            ('locked', 'Bloqueada'),
            ('error', 'Error'),
            ('unsign', 'No Timbrada'),
            ('signed', 'Timbrada')
        ]
    )

    _order = 'name ASC'

    def gen_name(self):
        return 'NOM/%s' % str(self.employee_id.old_id).zfill(4)

    @api.model
    def create(self, vals):

        rec = super(hr_paysheet, self).create(vals)

        if not rec.name:

            rec.sudo().write({
                'name': rec.gen_name()
            })

        return rec

    def find_input(self, concept):

        """
        Find input in registered paysheet inputs
        @param find_input: Paysheet input object.

        @return: Found input object.
        """

        for paysheet_input in self.inputs_ids:

            if(concept.id == paysheet_input.concept_id.id):

                return paysheet_input

        return False

    @api.onchange('last_paysheet')
    def _change_last_paysheet(self):

        self.struct_id = self.env['hr.paysheet.struct'].search([('internal_type', '=', 'F')], limit=1).id if self.last_paysheet else False
        self.ant_bonus_days = 12 if self.last_paysheet else False
        self.month_worked_days = 12 if self.last_paysheet else False

        if self.last_paysheet:
            self.employee_id.update_holidays()
            self.pending_holidays = self.employee_id.total_holidays
        else:
            self.pending_holidays = 0

    @api.onchange('leave_reward')
    def _change_leave_reward(self):

        self.leave_reward_days = 90 if self.leave_reward else 0

    @api.onchange('reward_days')
    def _change_reward_days(self):

        self.reward_days_amount = 20 if self.reward_days else 0

    @api.onchange('reward_months')
    def _change_reward_months(self):

        self.reward_months_amount = 90 if self.reward_months else 0

    @api.multi
    def action_calculate(self):

        """
        Calculate the paysheet rules.
        """

        # SET DEAFULT ENCODING AS UTF-8
        reload(sys)
        sys.setdefaultencoding('utf-8')

        # Reset paysheet trades
        self.trade_ids.sudo().unlink()

        # Update benefits
        self.contract_id.update_benefits(self.lot_id.to_date)

        # Load inputs
        inputs = PaysheetInputs()
        inputs_map = {}

        for input_id in self.inputs_ids:
            inputs_map[input_id.concept_id.id] = input_id.amount
            setattr(inputs, input_id.code, input_id.amount)

        # INIT
        self.env['hr.paysheet.rule'].update_dict({
            'categories': PaysheetCategories(),
            'category': self.env['hr.paysheet.category'],
            'paysheet_id': self.id,
            'paysheet_leave_date': self.leave_date,
            'paysheet_pending_holidays': self.pending_holidays,
            'paysheet_ant_bonus_days': self.ant_bonus_days,
            'paysheet_leave_reward': self.leave_reward,
            'paysheet_leave_reward_days': self.leave_reward_days,
            'paysheet_reward_days': self.reward_days,
            'paysheet_reward_days_amount': self.reward_days_amount,
            'paysheet_payment_date': self.payment_date,
            'contract': self.contract_id,
            'employee': self.employee_id,
            'inputs': inputs,
            'logger': _logger,
            'rules': PaysheetRules(),
            'tables': self.env['hr.rank.table'],
            'tools': PaysheetTools(),
            'period': self.lot_id.period_id,
            'lot_from_date': self.lot_id.from_date,
            'lot_to_date': self.lot_id.to_date,
            'lot_company_id': self.lot_id.company_id.id,
            'payments': self.env['hr.periodic.payment']
        })

        # Check ignore trades
        ignore_trades = [ignore_id.id for ignore_id in self.ignore_ids]

        # Calculate rules
        rules  = self.env['hr.paysheet.rule'].search([('vtype', '=', 'G')])
        rules += self.struct_id.rule_ids if self.last_paysheet else self.lot_id.struct_id.rule_ids

        # CALCULATE RULES
        for rule in rules:

            # CHECK IGNORE RULES
            if rule.concept_id.id in ignore_trades:
                continue

            # CALCULATE RULE
            if rule.input_priority and rule.concept_id.id in inputs_map.keys():
                res = inputs_map[rule.concept_id.id]
            else:

                if(not rule.check()):
                    continue

                res = rule.calculate()

            # CHECK ZERO
            if rule.ignore_zero and res == 0:
                continue

            # RULE FREE LIMIT
            if rule.has_free_limit:

                free_limit = rule.calculate_free_limit()
                free_amount = min(free_limit, res)
                free_concept = rule.concept_id.free_concept_id
                tax_concept = rule.concept_id.tax_concept_id

                if free_amount > 0 and free_concept.id and (free_concept.id not in ignore_trades):

                    self.env['hr.paysheet.trade'].create({
                        'concept_id': free_concept.id,
                        'amount': free_amount,
                        'paysheet_id': self.id
                    })

                tax_amount = res - free_amount

                if tax_amount > 0 and tax_concept.id and (tax_concept.id not in ignore_trades):

                    self.env['hr.paysheet.trade'].create({
                        'concept_id': tax_concept.id,
                        'amount': tax_amount,
                        'paysheet_id': self.id
                    })

            if rule.concept_id.id:

                trade = self.env['hr.paysheet.trade'].search([('paysheet_id', '=', self.id), ('concept_id', '=', rule.concept_id.id)], limit=1)

                if trade.id:
                    trade.write({
                        'amount': trade.amount + res if rule.replace_method == 'ADD' else res
                    })
                    continue

            if rule.concept_id.id:

                self.env['hr.paysheet.trade'].create({
                    'concept_id': rule.concept_id.id,
                    'amount': res,
                    'paysheet_id': self.id
                })

        if self.amount_by_type('DED') > self.amount_by_type('PER'):
            raise UserError('Nómina con saldo negativo %s' % self.name)

        self.env.cr.execute("""
            SELECT (
                SELECT COALESCE(SUM(ABS(amount)), 0)
                FROM hr_paysheet_trade pt
                INNER JOIN hr_paysheet_concept pc ON pt.concept_id = pc.id
                WHERE pc.ctype = 'PER'
                AND pc.printable = TRUE
                AND pt.paysheet_id = {pid}
            ) AS perceptions,
            (
                SELECT COALESCE(SUM(ABS(amount)), 0)
                FROM hr_paysheet_trade pt
                INNER JOIN hr_paysheet_concept pc ON pt.concept_id = pc.id
                WHERE pc.ctype = 'DED'
                AND pc.printable = TRUE
                AND pt.paysheet_id = {pid}
            ) AS deductions
        """.format(pid=self.id))

        totals = self.env.cr.fetchone()

        self.perceptions = totals[0]
        self.deductions = totals[1]


    @api.multi
    def action_cfdi_sent(self):
        """
        Check send CFDI option for each paysheet
        """

        for paysheet in self.browse(self.env.context.get('active_ids', False)):

            if paysheet.state not in ('signed'):
                continue

            paysheet.check_cfdi_send()

    @api.multi
    def action_unsign(self):
        """
        Change status to unsign
        """

        self.state = 'unsign'


    def __format_xml_template(self, values):

        # SET DEAFULT ENCODING AS UTF-8
        reload(sys)
        sys.setdefaultencoding('utf-8')

        return """<?xml version="1.0" encoding="UTF-8"?>
<cfdi:Comprobante xmlns:cfdi="http://www.sat.gob.mx/cfd/3" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:nomina12="http://www.sat.gob.mx/nomina12" xsi:schemaLocation="http://www.sat.gob.mx/cfd/3 http://www.sat.gob.mx/sitio_internet/cfd/3/cfdv33.xsd http://www.sat.gob.mx/nomina12 http://www.sat.gob.mx/sitio_internet/cfd/nomina/nomina12.xsd" Version="3.3" Serie="{company_short_name}" Folio="{folio}" Fecha="{current_date}" FormaPago="{payment_form}" SubTotal="{perceptions}" Descuento="{deductions}" Moneda="{currency}" Total="{total}" TipoDeComprobante="{voucher_type}" MetodoPago="{payment_type}" LugarExpedicion="{expedition_place}">
  <cfdi:Emisor Rfc="{company_rfc}" Nombre="{company_name}" RegimenFiscal="{company_regime}"/>
  <cfdi:Receptor Rfc="{employee_rfc}" Nombre="{employee_name}" UsoCFDI="P01"/>
  <cfdi:Conceptos>
    <cfdi:Concepto ClaveProdServ="84111505" Cantidad="1" ClaveUnidad="ACT" Descripcion="Pago de nómina" ValorUnitario="{perceptions}" Importe="{perceptions}" Descuento="{deductions}"/>
  </cfdi:Conceptos>
  <cfdi:Complemento>
    <nomina12:Nomina Version="{cfdi_version}" FechaPago="{payment_date}" FechaInicialPago="{from_date}" FechaFinalPago="{to_date}" NumDiasPagados="{worked_days}" TipoNomina="{paysheet_type}" {total_deductions} {total_other_payments} {total_perceptions}>
      <nomina12:Emisor RegistroPatronal="{employer_registration}"/>
      <nomina12:Receptor Curp="{employee_curp}" TipoContrato="{contract_type}" TipoRegimen="{regime_type}" NumEmpleado="{employee_old_id}" PeriodicidadPago="{payment_period}" ClaveEntFed="{state_key}" NumSeguridadSocial="{nss}" Banco="{bank_key}" {bank_account} FechaInicioRelLaboral="{start_work_date}" Antigüedad="{antique_time}" Departamento="{department}" Puesto="{job_name}" SalarioBaseCotApor="{wage}" RiesgoPuesto="{work_risk}" SalarioDiarioIntegrado="{sdi}" TipoJornada="{work_type}"/>{paysheet_str}
    </nomina12:Nomina>
  </cfdi:Complemento>
</cfdi:Comprobante>""".format(**values)

    def __process_xml_values(self):

        # SET SYSTEM TIMEZONE
        os.environ['TZ'] = "America/Mexico_City"

        # PROCESS VALUES
        employee = self.sudo().employee_id
        company  = self.sudo().lot_id.company_id
        current_date = datetime.now()
        isr = self.concept_amount('code', 20)
        # ANTIQUE TIME
        register_date = datetime.strptime(employee.in_date, DEFAULT_SERVER_DATE_FORMAT)
        payment_date = datetime.strptime(self.lot_id.to_date, DEFAULT_SERVER_DATE_FORMAT)
        antique_time = payment_date - register_date
        antique_years = antique_time.days / 365.25
        antique_years_dec = antique_years - int(antique_years)
        antique_years += 1 if antique_years_dec > 0.5 else 0

        # RETRIEVE PAYSHEET TOTALS
        self.env.cr.execute("""
            SELECT (
                SELECT COALESCE(SUM(ABS(amount)), 0)
                FROM hr_paysheet_trade pt
                INNER JOIN hr_paysheet_concept pc ON pt.concept_id = pc.id
                INNER JOIN hr_paysheet_sat_concept sc ON pc.sat_concept_id = sc.id
                WHERE pc.ctype = 'PER'
                AND pc.printable = TRUE
                AND pt.paysheet_id = {pid}
            ) AS perceptions,
            (
                SELECT COALESCE(SUM(ABS(amount)), 0)
                FROM hr_paysheet_trade pt
                INNER JOIN hr_paysheet_concept pc ON pt.concept_id = pc.id
                INNER JOIN hr_paysheet_sat_concept sc ON pc.sat_concept_id = sc.id
                WHERE pc.ctype = 'DED'
                AND pc.printable = TRUE
                AND pt.paysheet_id = {pid}
            ) AS deductions,
            (
                SELECT COALESCE(SUM(ABS(amount)), 0)
                FROM hr_paysheet_trade pt
                INNER JOIN hr_paysheet_concept pc ON pt.concept_id = pc.id
                WHERE pc.other_payments = TRUE
                AND pc.printable = TRUE
                AND pt.paysheet_id = {pid}
            ) AS other_payments
        """.format(pid=self.id))

        totals = self.env.cr.fetchone()

        # RETRIEVE PAYSHEET BODY STRING
        base_query = """
            SELECT pc.code, pc.name, abs(pt.amount), free_concept_id, tax_concept_id, sc.code, pc.other_payments_type, sc.name, pc.id
            FROM hr_paysheet_trade pt
            INNER JOIN hr_paysheet_concept pc ON pt.concept_id = pc.id
            INNER JOIN hr_paysheet_sat_concept sc ON pc.sat_concept_id = sc.id
            WHERE pc.{type}
            AND pc.printable = TRUE
            AND pt.paysheet_id = {pid}
        """

        self.env.cr.execute(base_query.format(type = "ctype = 'PER'", pid = self.id))

        paysheet_str = ''
        perception_rows = self.env.cr.fetchall()
        perceptions_free = perceptions_tax = 0

        self.env.cr.execute("""
            SELECT COALESCE(SUM(ABS(pt.amount)), 0)
            FROM hr_paysheet_trade pt
            INNER JOIN hr_paysheet_concept pc ON pt.concept_id = pc.id
            INNER JOIN hr_paysheet_sat_concept sc ON pc.sat_concept_id = sc.id
            WHERE sc.code IN ('022', '023', '025')
            AND pt.paysheet_id = %s
        """ % self.id)

        compensation_amount = self.env.cr.fetchone()[0]

        if len(perception_rows) > 0:

            perceptions_str = '\n      <nomina12:Percepciones TotalSueldos="{wage_amount}" {total_compensation} TotalGravado="{per_tax}" TotalExento="{per_free}">'

            # BUILD PERCEPTIONS STRING
            for perception in perception_rows:

                free_amount = tax_amount = 0

                if perception[3] or perception[4]:

                    if(perception[3]):
                        free_amount = self.concept_amount('id', perception[3])

                    if(perception[4]):
                        tax_amount = self.concept_amount('id', perception[4])

                else:

                    if perception[8] in self.category_concept_ids('BISPT'):
                        tax_amount = perception[2]
                    else:
                        free_amount = perception[2]

                perceptions_free += free_amount
                perceptions_tax += tax_amount

                if perception[5] in ('022', '023', '025'):
                    continue

                perceptions_str += '\n        <nomina12:Percepcion TipoPercepcion="{st_code}" Clave="{code}" Concepto="{name}" ImporteExento="{free_amount}" ImporteGravado="{tax_amount}"/>'.format(code=str(perception[0]).zfill(3), name=perception[1] or perception[1], free_amount="%.2f" % free_amount, tax_amount="%.2f" % tax_amount, st_code=perception[5])

            # BUILD COMPENSATIONS STRING
            if compensation_amount > 0:

                perceptions_str += '\n'

                compensation_tax = 0

                for perception in perception_rows:

                    if perception[5] not in ('022', '023', '025'):
                        continue

                    free_amount = tax_amount = 0

                    if perception[3] or perception[4]:

                        if(perception[3]):
                            free_amount = self.concept_amount('id', perception[3])

                        if(perception[4]):
                            tax_amount = self.concept_amount('id', perception[4])

                    else:

                        if perception[8] in self.category_concept_ids('BISPT'):
                            tax_amount = perception[2]
                        else:
                            free_amount = perception[2]

                    compensation_tax += tax_amount

                    perceptions_str += '\n        <nomina12:Percepcion TipoPercepcion="{st_code}" Clave="{code}" Concepto="{name}" ImporteExento="{free_amount}" ImporteGravado="{tax_amount}"/>'.format(code=str(perception[0]).zfill(3), name=perception[1] or perception[1], free_amount="%.2f" % free_amount, tax_amount="%.2f" % tax_amount, st_code=perception[5])

                last_month_amount = self.last_month_amount(self.lot_id.payment_date, 'PER') - self.last_month_amount(self.lot_id.payment_date, 'DED')

                perceptions_str += '\n        <nomina12:SeparacionIndemnizacion TotalPagado="{amount}" NumAñosServicio="{worked_years}" UltimoSueldoMensOrd="{month_wage}" IngresoAcumulable="{acc_amount}" IngresoNoAcumulable="{no_acc_amount}"/>'.format(
                    worked_years=int(antique_years),
                    amount="%.2f" % compensation_amount,
                    month_wage="%.2f" % last_month_amount,
                    acc_amount="%.2f" % min(compensation_tax, last_month_amount),
                    no_acc_amount="%.2f" % max(0, compensation_tax - last_month_amount)
                )

            perceptions_str += '\n      </nomina12:Percepciones>'

            paysheet_str += perceptions_str.format(per_free="%.2f" % perceptions_free, per_tax="%.2f" % perceptions_tax, wage_amount= "%.2f" % (totals[0] - compensation_amount), total_compensation='TotalSeparacionIndemnizacion="%.2f"' % compensation_amount if compensation_amount > 0 else ' ')


        self.env.cr.execute(base_query.format(type = "ctype = 'DED'", pid = self.id))

        deductions_str = ''
        deductions_rows = self.env.cr.fetchall()
        deductions_free = deductions_tax = 0

        if len(deductions_rows) > 0:

            deductions_str = '\n      <nomina12:Deducciones TotalOtrasDeducciones="{other_deductions}" {ispt}>'.format(ispt=('TotalImpuestosRetenidos="%.2f"' % isr if isr > 0 else ' '), other_deductions="%.2f" % ( totals[1] - isr ))

            for deduction in deductions_rows:

                free_amount = tax_amount = 0

                if(deduction[3]):
                    free_amount = self.concept_amount('id', deduction[3])

                if(deduction[4]):
                    tax_amount = self.concept_amount('id', deduction[4])

                if(not (deduction[3] and deduction[4])):
                    tax_amount = deduction[2]

                deductions_free += free_amount
                deductions_tax += tax_amount

                deductions_str += '\n        <nomina12:Deduccion TipoDeduccion="{st_code}" Clave="{code}" Concepto="{name}" Importe="{tax_amount}"/>'.format(code=str(deduction[0]).zfill(3), name=deduction[1], tax_amount="%.2f" % deduction[2], st_code=deduction[5])

            deductions_str += '\n      </nomina12:Deducciones>'

            paysheet_str += deductions_str.format(ded_free="%.2f" % deductions_free, ded_tax="%.2f" % deductions_tax)


        self.env.cr.execute("""
            SELECT pc.code, pc.name, abs(pt.amount), pc.other_payments_type
            FROM hr_paysheet_trade pt
            INNER JOIN hr_paysheet_concept pc ON pt.concept_id = pc.id
            WHERE pc.other_payments = TRUE
            AND pc.printable = TRUE
            AND pt.paysheet_id = %s
        """ % self.id)

        other_payments_str = ''
        other_payments_rows = self.env.cr.fetchall()
        other_payments_free = other_payments_tax = 0

        if len(other_payments_rows) > 0:

            other_payments_str = '\n      <nomina12:OtrosPagos>'

            for other_payment in other_payments_rows:

                if other_payment[3] == '002':
                    other_payments_str += '\n        <nomina12:OtroPago TipoOtroPago="{st_code}" Clave="{code}" Concepto="{name}" Importe="{tax_amount}">'
                    other_payments_str += '\n           <nomina12:SubsidioAlEmpleo SubsidioCausado="{tax_amount}"/>'
                    other_payments_str += '\n        </nomina12:OtroPago>'
                    other_payments_str  = other_payments_str.format(code=str(other_payment[0]).zfill(3), name=other_payment[1], tax_amount="%.2f" % other_payment[2], st_code=other_payment[3])
                else:
                    other_payments_str += '\n        <nomina12:OtroPago TipoOtroPago="{st_code}" Clave="{code}" Concepto="{name}" Importe="{tax_amount}"/>'
                    other_payments_str  = other_payments_str.format(code=str(other_payment[0]).zfill(3), name=other_payment[1], tax_amount="%.2f" % other_payment[2], st_code=other_payment[3])

            other_payments_str += '\n      </nomina12:OtrosPagos>'

            paysheet_str += other_payments_str

        # CHECK INHABILITIES
        inh_total = self.concepts_amount((39,40))
        inh = self.env['hr.ss.move'].search([('employee_id', '=', self.employee_id.id), ('to_date', '>=', self.lot_id.from_date)], limit=1)

        if inh_total > 0 and inh.id:
            inh_str = '\n      <nomina12:Incapacidades>'
            inh_str += '\n        <nomina12:Incapacidad DiasIncapacidad="%s" TipoIncapacidad="%s"/>' % (int(inh_total), inh.inhability_type.zfill(2))
            inh_str += '\n      </nomina12:Incapacidades>'
            paysheet_str += inh_str

        # CHECK EXTRA HOURS
        he_total = self.concepts_amount(27)

        if he_total > 0:
            he_num = int(self.concepts_amount(71))
            days = 0

            if he_num > 1:
                days = 1

            if he_num > 3:
                days = 2

            if he_num > 6:
                days = 3

            he_str = '\n      <nomina12:HorasExtras>'
            he_str += '\n        <nomina12:HorasExtra Dias="%s" TipoHoras="Dobles" HorasExtra="%s" ImportePagado="%s"/>' % (days, he_num, '%.2f' % he_total)
            he_str += '\n      </nomina12:HorasExtras>'
            paysheet_str += he_str


        weeks = antique_time.days / 7
        worked_days = self.concept_amount('code', 34) + ((self.concept_amount('code', 65) + self.concept_amount('code', 36)) * 7.0 / 6.0) + self.concept_amount('code', 110)

        values = {
            'antique_time': 'P%sW' % weeks,
            'bank_account': 'CuentaBancaria="%s"' % employee.bank_account if employee.bank_account else ' ',
            'bank_key': employee.bank_id.bic,
            'cfdi_version': '1.2',
            'company_name': company.name,
            'company_regime': company.regime_id.name,
            'company_rfc': company.rfc,
            'company_short_name': company.short_name,
            'contract_type': self.contract_id.type_id.code,
            'currency': 'MXN',
            'currency_type': '1',
            'current_date': str(current_date.isoformat())[:19],
            'deductions': "%.2f" % totals[1],
            'department': employee.department_id.name,
            'employee_curp': employee.curp,
            'employee_name': employee.name,
            'employee_old_id': employee.old_id,
            'employee_rfc': employee.rfc,
            'employer_registration':  employee.employer_registration.name,
            'expedition_place': employee.employer_registration.zip_code,
            'folio': '%s%s' % (str(self.lot_id.old_id).zfill(4), str(employee.old_id).zfill(4)),
            'from_date': self.lot_id.from_date,
            'job_name': employee.job_id.name,
            'nss': employee.ssn,
            'payment_date': self.payment_date or self.lot_id.payment_date,
            'payment_form': '99',
            'payment_period': self.lot_id.struct_id.period,
            'payment_type': 'PUE',
            'paysheet_str': paysheet_str,
            'paysheet_type': self.lot_id.struct_id.stype,
            'perceptions': "%.2f" % (totals[0] + totals[2]),
            'regime_type': employee.contract_regime_id.code,
            'sdi': "%.2f" % self.contract_id.sdi,
            'start_work_date': employee.in_date,
            'state_key': employee.work_state_id.code,
            'to_date': self.lot_id.to_date,
            'total': "%.2f" % ((totals[0] + totals[2]) - totals[1]),
            'total_deductions': 'TotalDeducciones="%.2f"' % totals[1] if totals[1] > 0 else ' ',
            'total_other_payments': 'TotalOtrosPagos="%.2f"' % totals[2] if totals[2] > 0 else ' ',
            'total_perceptions': 'TotalPercepciones="%.2f"' % totals[0] if totals[0] > 0 else ' ',
            'version': '3.3',
            'voucher_type': 'N',
            'wage': "%.2f" % self.contract_id.sdi,
            'work_risk': employee.employer_registration.risk_id.code,
            'work_type': employee.work_type,
            'worked_days': "%.3f" % worked_days if worked_days > 0 else '1',
        }

        # CHECK REQUIRED
        for key in values:
            if not values[key]:
                raise UserError('RF001 - VALOR REQUERIDO NO ENCONTRADO: %s => %s' % (self.name, key))

        return values

    def generate_xml(self):
        """
        Generate XML CFDI file
        """

        if self.state not in ('locked','error'):
            return False

        values = self.__process_xml_values()

        try:
            xml = self.__format_xml_template(values)
        except Exception as e:
            raise UserError('XML001 - Error al formar el archivo XML: %s' % e)

        return xml

    @api.multi
    def action_sign(self, context = {}, sign_task = False):
        """
            Calculate each hr.paysheet related record
        """

        os.environ['TZ'] = "America/Mexico_City"
        paysheets_count = len(self)
        gen_count = 0
        signed_count = 0

        if not sign_task:

            sign_task = self.env['cfdi.sign.task'].sudo().create({
                'company_id': self[0].lot_id.company_id.id
            })
            sign_task.prepare()

        # GENERATE XML FILES
        for paysheet in self:

            if paysheet.state not in ('locked','error'):
                continue

            gen_xml_id = paysheet.cfdi_ids.search([('paysheet_id', '=', paysheet.id), ('state', '=', 'generated')], limit=1)

            if not gen_xml_id.id:

                signed_xml = sign_task.stamp_xml(paysheet.generate_xml())

                gen_xml_id = self.env['hr.xml.cfdi'].create({
                    'name': 'GEN: %s - %s' % (paysheet.employee_id.rfc, paysheet.lot_id.company_id.rfc),
                    'file_id': self.env['data.filemanager'].save_base64(base64.b64encode(signed_xml), 'gen_xml_cfdi.xml'),
                    'paysheet_id': paysheet.id
                })

            if gen_count % 10 == 0:
                _logger.debug("GENERATE %s OF %s" % (gen_count, paysheets_count))

            gen_count += 1

            self.env.cr.commit()

        # SIGN PAYSHEETS
        for paysheet in self:

            gen_xml_id = paysheet.cfdi_ids.search([('paysheet_id', '=', paysheet.id), ('state', '=', 'generated')], limit=1)

            if not gen_xml_id.id:
                continue

            response = sign_task.sign_xml(gen_xml_id.parse_xml(False))

            if response.has('xml'):

                xml_cfdi = ET.fromstring(response.xml.decode('base64').encode('UTF-8'))

                xml_tfd = xml_cfdi.find('.//{http://www.sat.gob.mx/TimbreFiscalDigital}TimbreFiscalDigital')
                xml_ps = xml_cfdi.find('.//{http://www.sat.gob.mx/nomina12}Nomina')
                xml_src = xml_cfdi.find('.//{http://www.sat.gob.mx/cfd/3}Emisor')
                xml_dst = xml_cfdi.find('.//{http://www.sat.gob.mx/cfd/3}Receptor')

                gen_xml_id.file_id.update_base64(response.xml, '%s.xml' % xml_tfd.get('UUID'))

                gen_xml_id.write({
                    'name': xml_tfd.get('UUID'),
                    'state': 'signed',
                    'send_date': xml_cfdi.get('Fecha').replace('T', ' '),
                    'cert_date': xml_tfd.get('FechaTimbrado').replace('T', ' '),
                    'amount': xml_cfdi.get('Total'),
                    'from_date': xml_ps.get('FechaInicialPago'),
                    'to_date': xml_ps.get('FechaFinalPago'),
                    'payment_date': xml_ps.get('FechaPago'),
                    'rfc_src':  xml_src.get('Rfc'),
                    'rfc_dst':  xml_dst.get('Rfc')
                })

                paysheet.cfdi_id = gen_xml_id.id
                paysheet.state = 'signed'
                paysheet.last_error = False

                paysheet.check_cfdi_send()

            if response.has('error'):

                paysheet.state = 'error'
                paysheet.last_error = '{0} - {1}'.format(response.error_code, response.error)

                _logger.error('SIGN ERROR: %s - %s => %s', response.error_code, response.error, paysheet.id)

                if response.error_code == 'LOST_CONNECTION':
                    raise UserError('No se pudo establecer la conexión con el servidor.')

            if signed_count % 10 == 0:
                _logger.debug("SIGN %s OF %s" % (signed_count, paysheets_count))

            signed_count += 1

            self.env.cr.commit()

    def _utc_to_tz(self, _date, _time_zone):

        # CONVER TO UTC
        _date = _date.replace(tzinfo = tz.gettz('UTC'))

        # LOAD TIMEZONE
        to_zone  = tz.gettz(_time_zone)

        return _date.astimezone(to_zone)

    def concept_amount(self, _field, _value):

        self.ensure_one()

        query = """
            SELECT COALESCE(SUM(ABS(amount)), 0)
            FROM hr_paysheet_trade pt
            INNER JOIN hr_paysheet_concept pc ON pt.concept_id = pc.id
            WHERE pc.{field} = {value}
            AND pt.paysheet_id = {pid}
        """

        self.env.cr.execute(query.format(pid=self.id, field=_field, value=_value))

        return self.env.cr.fetchone()[0]

    def amount_by_type(self, _type):

        self.ensure_one()

        query = """
            SELECT COALESCE(SUM(ABS(amount)), 0)
            FROM hr_paysheet_trade pt
            INNER JOIN hr_paysheet_concept pc ON pt.concept_id = pc.id
            WHERE pc.printable = TRUE AND pc.ctype = '{type}'
            AND pt.paysheet_id = {pid}
        """

        self.env.cr.execute(query.format(pid=self.id, type=_type))

        return self.env.cr.fetchone()[0]

    def year_amount(self, _codes = ()):

        codes = _codes if type(_codes) is int else ','.join(str(code) for code in _codes)

        query = """
            SELECT COALESCE(ABS(SUM(amount)), 0)
            FROM hr_paysheet_trade pt
            INNER JOIN hr_paysheet ps ON pt.paysheet_id = ps.id
            INNER JOIN hr_paysheet_lot psl ON ps.lot_id = psl.id
            INNER JOIN hr_paysheet_concept pc ON pt.concept_id = pc.id
            WHERE EXTRACT(ISOYEAR FROM psl.payment_date) = %s
            AND ps.employee_id = %s
            AND pc.code IN (%s)
        """ % (datetime.today().year, self.employee_id.id, codes)

        self.env.cr.execute(query)

        return self.env.cr.fetchone()[0]

    def concepts_amount(self, _codes):

        codes = _codes if type(_codes) is int else ','.join(str(code) for code in _codes)

        query = """
            SELECT COALESCE(SUM(ABS(amount)), 0)
            FROM hr_paysheet_trade pt
            INNER JOIN hr_paysheet_concept pc ON pt.concept_id = pc.id
            WHERE pc.code IN (%s)
            AND pt.paysheet_id = %s
        """

        self.env.cr.execute(query % (codes, self.id))

        return self.env.cr.fetchone()[0]

    def locale_format(self, _date, _format, _capital = False, _position = 3, _locale = 'es_MX.UTF-8'):

        # Convenrt date to locale format
        locale.setlocale(locale.LC_TIME, _locale)

        res = _date.strftime(_format)

        if(_capital):
            s = list(res)
            s[_position] = s[_position].upper()
            res = "".join(s)

        return res

    def parse_date(self, _date, _time_zone = "America/Mexico_City"):

        # CURRENT DATE
        return datetime.strptime(_date, DEFAULT_SERVER_DATE_FORMAT)

    def rows_by_type(self, _type):

        base_query = """
            SELECT pc.code, pc.name, abs(pt.amount)
            FROM hr_paysheet_trade pt
            INNER JOIN hr_paysheet_concept pc ON pt.concept_id = pc.id
            WHERE pc.ctype = '{type}'
            AND pc.printable = TRUE
            AND pt.paysheet_id = {pid}
            ORDER BY pc.code ASC
        """

        self.env.cr.execute(base_query.format(type = _type, pid = self.id))

        return self.env.cr.fetchall()

    def get_voucher_label(self):

        if self.lot_id.ltype == 'ES':
            return self.lot_id.paycheck_text

        return 'Periodo: %s a %s' % (
            self.locale_format(self.parse_date(self.lot_id.from_date), '%d/%b/%Y'),
            self.locale_format(self.parse_date(self.lot_id.to_date), '%d/%b/%Y')
        )

    def category_concept_ids(self, category_code):

        self.env.cr.execute("""
            SELECT hr_paysheet_concept_id FROM hr_paysheet_category_hr_paysheet_concept_rel pcr
            INNER JOIN hr_paysheet_category pc ON pcr.hr_paysheet_category_id = pc.id
            WHERE pc.code = '%s'
        """ % category_code)

        return [row[0] for row in self.env.cr.fetchall()]


    def last_month_amount(self, _date, _type):

        base_date = datetime.strptime(_date, DEFAULT_SERVER_DATE_FORMAT)

        # REWIND MONTH
        _month = 12 if base_date.month == 1 else base_date.month - 1
        _year = base_date.year - 1 if base_date.month == 1 else base_date.year

        base_date = base_date.replace(month=_month, year=_year)

        last_day = calendar.monthrange(base_date.year, base_date.month)[1]
        from_date = base_date.replace(day=1).isoformat()[:10]
        to_date = base_date.replace(day=last_day).isoformat()[:10]

        query = """
            SELECT COALESCE(SUM(ABS(amount)), 0)
            FROM hr_paysheet_trade pt
            INNER JOIN hr_paysheet ps ON pt.paysheet_id = ps.id
            INNER JOIN hr_paysheet_lot psl ON ps.lot_id = psl.id
            INNER JOIN hr_paysheet_concept pc ON pt.concept_id = pc.id
            WHERE psl.payment_date >= '%s' AND psl.payment_date <= '%s'
            AND ps.employee_id = %s
            AND pc.ctype = '%s'
        """ % (from_date, to_date, self.employee_id.id, _type)

        self.env.cr.execute(query)

        return self.env.cr.fetchone()[0]

    def acc_by_month(self, _codes, _date = False):

        codes = _codes if type(_codes) is int else ','.join(str(code) for code in _codes)
        base_date = datetime.strptime(_date, DEFAULT_SERVER_DATE_FORMAT) if _date else datetime.today()

        last_day = calendar.monthrange(base_date.year, base_date.month)[1]
        from_date = base_date.replace(day=1).isoformat()[:10]
        to_date = base_date.replace(day=last_day).isoformat()[:10]

        query = """
            SELECT COALESCE(SUM(ABS(amount)), 0)
            FROM hr_paysheet_trade pt
            INNER JOIN hr_paysheet ps ON pt.paysheet_id = ps.id
            INNER JOIN hr_paysheet_lot psl ON ps.lot_id = psl.id
            INNER JOIN hr_paysheet_concept pc ON pt.concept_id = pc.id
            WHERE psl.payment_date >= '%s' AND psl.payment_date <= '%s'
            AND ps.employee_id = %s
            AND pc.code IN (%s)
        """ % (from_date, to_date, self.employee_id.id, codes)

        self.env.cr.execute(query)

        return self.env.cr.fetchone()[0]

    def acc_by_year(self, _year, _codes):

        year_id = self.env['hr.paysheet.year'].search([('name', '=', str(_year))], limit=1)

        if not year_id:
            return 0

        codes = ','.join(str(code) for code in _codes.split(','))

        query = """
            SELECT COALESCE(SUM(ABS(amount)), 0)
            FROM hr_paysheet_trade pt
            INNER JOIN hr_paysheet hp ON pt.paysheet_id = hp.id
            INNER JOIN hr_paysheet_lot hpl ON hp.lot_id = hpl.id
            INNER JOIN hr_paysheet_concept pc ON pt.concept_id = pc.id
            WHERE hp.employee_id = %s AND pt.year_id = %s AND pc.code IN (%s)
        """ % (self.employee_id.id, year_id.id if year_id else -1, codes)

        self.env.cr.execute(query)

        return self.env.cr.fetchone()[0]

    def check_cfdi_send(self):

        self.ensure_one()

        if self.employee_id.cfdi_send and self.employee_id.cfdi_mail_ok and self.employee_id.cfdi_mail:
            self.send_cfdi = True

class PaysheetRules():
    """
    Paysheet rules container
    """
    pass

class PaysheetInputs():
    """
    Paysheet inputs container
    """
    pass

class PaysheetPayments():
    """
    Paysheet payments container
    """
    pass

class PaysheetCategories():
    """
    Paysheet categories container
    """
    pass

class PaysheetTools():
    """
    Paysheet calc tools
    """

    def date_diff(self, date_from, date_to):
        """
        CALCULATE DATE DIFF IN DAYS

        @param date_from (str): intial date
        @param date_to (str): last date
        """

        # PARSE DATES
        dfrom = datetime.strptime(date_from, DEFAULT_SERVER_DATE_FORMAT)
        dto   = datetime.strptime(date_to, DEFAULT_SERVER_DATE_FORMAT)

        return (dto - dfrom).days

    def trunc_decimals(self, value, places):
        """
        Trunc number to decimal places

        @param value (float): decimal number to trunc
        @param places (int): number of places
        """

        if(value == 0):
            return 0

        ret = ''

        abs_int = abs(int(value))

        decimal = str(abs(abs(int(value)) - abs(value)))[2:]

        if(value < 0):
            ret += '-'

        if(places > 0):
            decimal = decimal[:places]

        ret += str(abs_int) + '.' + decimal

        return float(ret)

    def check_attribute(self, obj, attr):
        """
        Check if object has attribute

        @param obj (obj): object to analize
        @param attr (str): attribute to find in the object

        @return (bool): hasattr function result
        """

        return hasattr(obj, attr)

    def randint(self, int1, int2):
        """
        Generate pseudorandom int in range
        """

        return random.randint(int1, int2)

    def today(self):
        """
        Return current date
        """

        return datetime.today()

    def parse_date(self, _date):
        """
        Return date string as object
        """

        return datetime.strptime(_date, DEFAULT_SERVER_DATE_FORMAT)

    def month_days(self, _year, _month):
        """
        Return days of month
        """

        return calendar.monthrange(_year, _month)[1]