# -*- coding: utf-8 -*-
# © <2016> <Omar Torres Silva (otorres@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import calendar
import logging
import os
import subprocess
import sys
import urllib
import uuid
from datetime import datetime
from lxml import etree as ET

from openerp import fields, models, api
from openerp.exceptions import Warning
from openerp.osv.orm import except_orm
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT

_logger = logging.getLogger(__name__)

class hr_council_lot(models.Model):
    _name = 'hr.council.lot'
    _description = 'HR COUNCIL LOT'

    def _default_from_date(self):
        return datetime.today().replace(day=1)

    def _default_to_date(self):
        current_date = datetime.today()
        last_day = calendar.monthrange(current_date.year, current_date.month)[1]
        return current_date.replace(day=last_day)

    def _default_payment_date(self):
        return datetime.today()

    name = fields.Char(
        string='Nombre',
        required=True
    )
    vouchers_count = fields.Integer(
        string='Recibos',
        compute='_vouchers_count',
    )
    voucher_ids = fields.One2many(
        string='Recibos',
        comodel_name='hr.council.voucher',
        inverse_name='lot_id'
    )
    from_date = fields.Date(
        string='Desde',
        default=_default_from_date
    )
    to_date = fields.Date(
        string='Hasta',
        default=_default_to_date
    )
    payment_date = fields.Date(
        string='Fecha de pago',
        default=_default_payment_date
    )
    last_error = fields.Text(
        string='Error'
    )
    state = fields.Selection(
        string='Estado',
        size=3,
        default='GEN',
        selection=[
            ('GEN', 'Generado'),
            ('SIG', 'Timbrado')
        ]
    )

    def _vouchers_count(self):
        """
            Count all hr.council.voucher related records
        """

        self.vouchers_count = self.voucher_ids.search_count([('lot_id', '=', self.id)])

    @api.multi
    def action_download(self):

        # SET SYSTEM TIMEZONE
        os.environ['TZ'] = "America/Mexico_City"

        base_path = '/tmp/council_lot_xml/%s' % uuid.uuid4()

        self.execute("mkdir -p %s" % base_path)

        for voucher in self.voucher_ids:
            f = open('%s/%s.xml' % (base_path, voucher.name), 'w')
            f.write(voucher.xml)
            f.close()

        filename = "RECIBOS_%s" % datetime.today().strftime('%m-%Y')

        self.execute("zip -j %s/%s %s/*" % (base_path, filename, base_path))

        return {
            'type' : 'ir.actions.act_url',
            'url': '/web/binary/zip_file_download?path=%s' % urllib.quote_plus("%s/%s.zip" % (base_path, filename)),
            'target': 'self',
        }

    @api.multi
    def action_generate(self):

        # SET SYSTEM TIMEZONE
        os.environ['TZ'] = "America/Mexico_City"

        # SET DEAFULT ENCODING AS UTF-8
        reload(sys)
        sys.setdefaultencoding('utf-8')

        self.voucher_ids.filtered(lambda r: r.state != 'SIG').unlink()

        for member in self.env['hr.council.member'].search([]):

            for payment in member.payment_ids:

                signed_voucher = self.voucher_ids.search([
                    ('lot_id', '=', self.id),
                    ('state', '=', 'SIG'),
                    ('member_id', '=', member.id),
                    ('company_id', '=', payment.company_id.id),
                ], limit=1)

                if not signed_voucher.id:

                    self.env['hr.council.voucher'].create({
                        'member_id': payment.member_id.id,
                        'lot_id': self.id,
                        'payment_date': datetime.today(),
                        'company_id': payment.company_id.id,
                        'xml': self.generate_xml(payment)
                    })

        for company_id in self.voucher_ids.filtered(lambda r: r.state != 'SIG').mapped('company_id'):

            sign_task = self.env['cfdi.sign.task'].sudo().create({
                'company_id': company_id.id
            })
            sign_task.prepare()

            for voucher in self.voucher_ids.filtered(lambda r: r.company_id.id == company_id.id and r.state != 'SIG'):

                voucher.xml = sign_task.stamp_xml(bytes(voucher.xml.decode('UTF-8')))

    @api.multi
    def action_sign(self):

        # SET SYSTEM TIMEZONE
        os.environ['TZ'] = "America/Mexico_City"

        # SET DEAFULT ENCODING AS UTF-8
        reload(sys)
        sys.setdefaultencoding('utf-8')

        for company_id in self.voucher_ids.filtered(lambda r: r.state != 'SIG').mapped('company_id'):

            sign_task = self.env['cfdi.sign.task'].sudo().create({
                'company_id': company_id.id
            })
            sign_task.prepare()

            for voucher in self.voucher_ids.filtered(lambda r: r.company_id.id == company_id.id and r.state != 'SIG'):

                response = sign_task.sign_xml(str(voucher.xml))

                if response.has('xml'):

                    xml_str = response.xml.decode('base64').encode('UTF-8')

                    xml_cfdi = ET.fromstring(xml_str)
                    tfd = xml_cfdi.xpath('//tfd:TimbreFiscalDigital', namespaces={"tfd": "http://www.sat.gob.mx/TimbreFiscalDigital"})

                    voucher.write({
                        'name': tfd[0].get('UUID'),
                        'xml': xml_str,
                        'state': 'SIG',
                        'last_error': False,
                        'folio': xml_cfdi.get('Folio')
                    })

                if response.has('error'):

                    voucher.state = 'ERR'
                    voucher.last_error = '{0} - {1}'.format(response.error_code, response.error)
                    _logger.error('SIGN ERROR: %s - %s => %s', response.error_code, response.error, voucher.member_id.name)

                    if response.error_code == 'LOST_CONNECTION':
                        raise except_orm('ERROR', 'No se pudo establecer la conexión con el servidor.')

                self.env.cr.commit()

        if len(self.voucher_ids.filtered(lambda r: r.state in ['ERR','GEN'])) == 0:
            self.state = 'SIG'

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
    <nomina12:Nomina Version="{cfdi_version}" TotalDeducciones="{total_deductions}" TotalPercepciones="{total_perceptions}" TipoNomina="O" FechaInicialPago="{from_date}" FechaFinalPago="{to_date}" NumDiasPagados="{payment_days}" FechaPago="{payment_date}">
      <nomina12:Receptor Curp="{employee_curp}" TipoRegimen="{regime_type}" ClaveEntFed="{state_key}" Banco="{bank_key}" NumEmpleado="999" TipoContrato="{contract_type}" CuentaBancaria="{bank_account}" PeriodicidadPago="{payment_period}"/>{paysheet_str}
    </nomina12:Nomina>
  </cfdi:Complemento>
</cfdi:Comprobante>""".format(**values)

    def __process_xml_values(self, payment):

        # SET SYSTEM TIMEZONE
        os.environ['TZ'] = "America/Mexico_City"

        TAX_PERCEPTION_CODES = {
            '3231': '038',
            '3442': '038',
            '3230': '046',
            '3745': '038'
        }

        perception_name = ''
        paysheet_str = ''

        for value in payment.CONCEPT_MAP:
            if value[0] == payment.concept:
                perception_name = value[1]

        perceptions_str = '\n      <nomina12:Percepciones TotalSueldos="{wage_amount}" TotalGravado="{per_tax}" TotalExento="{per_free}">'
        perceptions_str += '\n        <nomina12:Percepcion TipoPercepcion="{st_code}" Clave="{code}" Concepto="{name}" ImporteExento="{free_amount}" ImporteGravado="{tax_amount}"/>'.format(code=payment.concept, name=perception_name, free_amount="0.00", tax_amount="%.2f" % payment.amount, st_code=TAX_PERCEPTION_CODES[payment.concept])
        perceptions_str += '\n      </nomina12:Percepciones>'
        paysheet_str += perceptions_str.format(per_free="0.00", per_tax="%.2f" % payment.amount, wage_amount= "%.2f" % payment.amount)

        deductions_str = ''
        deductions_str = '\n      <nomina12:Deducciones TotalOtrasDeducciones="{other_deductions}" TotalImpuestosRetenidos="{ispt}">'.format(ispt="%.2f" % payment.tax_amount, other_deductions="%.2f" % payment.state_tax)
        deductions_str += '\n        <nomina12:Deduccion TipoDeduccion="002" Clave="020" Concepto="ISR" Importe="{tax_amount}"/>'.format(tax_amount="%.2f" % payment.tax_amount)

        if payment.state_tax > 0:
            deductions_str += '\n        <nomina12:Deduccion TipoDeduccion="004" Clave="000" Concepto="Impuesto Estatal" Importe="{tax_amount}"/>'.format(tax_amount="%.2f" % payment.state_tax)

        deductions_str += '\n      </nomina12:Deducciones>'
        paysheet_str += deductions_str

        folio_sequence = self.env['ir.sequence'].sudo().search([('name', '=', 'COUNCIL_VOUCHERS')], limit=1)

        values = {
            'bank_account': payment.bank_account,
            'bank_key': payment.bank_id.bic,
            'cfdi_version': '1.2',
            'company_name': payment.company_id.name,
            'company_regime': payment.company_id.regime_id.name,
            'company_rfc': payment.company_id.rfc,
            'company_short_name': 'HC',
            'contract_type': payment.member_id.contract_type_id.code,
            'currency': 'MXN',
            'currency_type': '1',
            'current_date': str(datetime.now().isoformat())[:19],
            'deductions': "%.2f" % (payment.tax_amount + payment.state_tax),
            'employee_curp': payment.member_id.curp,
            'employee_name': payment.member_id.name,
            'employee_rfc': payment.member_id.rfc,
            'expedition_place': payment.member_id.zip_code,
            'folio': folio_sequence._next(),
            'from_date': self.from_date,
            'to_date': self.to_date,
            'payment_days': (datetime.strptime(self.to_date, DEFAULT_SERVER_DATE_FORMAT) - datetime.strptime(self.from_date, DEFAULT_SERVER_DATE_FORMAT)).days + 1,
            'payment_date': str(datetime.today().isoformat())[:10],
            'payment_form': '99',
            'payment_period': payment.member_id.period,
            'payment_type': 'PUE',
            'paysheet_str': paysheet_str,
            'perceptions': "%.2f" % payment.amount,
            'regime_type': payment.member_id.regime_id.code,
            'state_key': payment.member_id.work_state_id.code,
            'total': "%.2f" % (payment.amount - (payment.tax_amount + payment.state_tax)),
            'total_deductions': "%.2f" % (payment.tax_amount + payment.state_tax),
            'total_perceptions': "%.2f" % payment.amount,
            'version': '3.2',
            'voucher_type': 'N',
        }

        # CHECK REQUIRED
        for key in values:
            if not values[key]:
                raise except_orm('RF001', 'VALOR REQUERIDO NO ENCONTRADO: %s => %s' % (payment.member_id.name, key))

        return values

    def generate_xml(self, payment):
        """
        Generate XML CFDI file
        """

        values = self.__process_xml_values(payment)

        try:
            xml = self.__format_xml_template(values)
        except Exception as e:
            raise Warning('XML001', 'Error al formar el archivo XML: %s' % e)

        return xml

    def execute(self, _command):
        try:
            return subprocess.check_output(_command, shell=True, stderr=subprocess.STDOUT)
        except Exception, e:
            _logger.error('EXECUTE ERROR: %s', e)
