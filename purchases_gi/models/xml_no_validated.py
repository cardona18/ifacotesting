# -*- coding: utf-8 -*-
# © <2017> <Juan Carlos VB (jcvazquez@gmail.com)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
import sys
import string
import base64
from datetime import date
from lxml import etree
import lxml.etree as ET
from lxml.etree import XMLSyntaxError
from xml.dom import minidom
import xml.etree.ElementTree
from io import StringIO
from xml.etree import ElementTree
from suds.client import Client
from openerp.exceptions import ValidationError
from odoo import _, api, fields, models, tools
from openerp.osv import osv

CFDI_SAT_QR_STATE = {
    'No Encontrado': 'not_found',
    'Cancelado': 'cancelled',
    'Vigente': 'valid',
}

_logger = logging.getLogger(__name__)


class xml_no_validated(models.Model):
    """
    Se creó el xml por qué se necesita en el módulo de compras para almacenar los CFDI de los proveedores.
    """
    _name = 'xml.no.validated'
    _inherit = ['mail.thread']

    name = fields.Char(
        string='Nombre',
        required=True
    )
    error_name = fields.Char(
        string='Descripción del error',
        required=True
    )

    xml_text = fields.Text(
        string='Texto xml',
    )

    rfc = fields.Char(
        string='RFC proveedor',
        required=True
    )
    rfc_company = fields.Char(
        string='RFC compañia',
    )
    order_id = fields.Many2one(
        string='Orden de compra',
        comodel_name='purchase.order',
        ondelete='cascade'
    )
    total_xml = fields.Float(
        string='Total del XML',
    )
    fecha_xml = fields.Char(
        string='Fecha xml',
    )
    folio_xml = fields.Char(
        string='Folio xml',
    )
    no_order = fields.Boolean(
        string='Sin orden de compra',
    )
    currency_name = fields.Text(
        string='Moneda',
    )

    @api.multi
    def update_sat_status(self, supplier_rfc, customer_rfc, total, uuid):
        '''
        Synchronize both systems: Odoo & SAT to make sure the invoice is valid.
        '''
        url = 'https://consultaqr.facturaelectronica.sat.gob.mx/ConsultaCFDIService.svc?wsdl'

        for inv in self:
            params = '"?re=%s&rr=%s&tt=%s&id=%s' % (
                tools.html_escape(tools.html_escape(supplier_rfc or '')),
                tools.html_escape(tools.html_escape(customer_rfc or '')),
                total or 0.0, uuid or '')
            try:
                response = Client(url).service.Consulta(params).Estado
            except Exception as e:
                _logger.error("ERROR: %s", str(e))
                continue

            inv.l10n_mx_edi_sat_status = CFDI_SAT_QR_STATE.get(response.__repr__(), 'none')

            return inv.l10n_mx_edi_sat_status

    def save_xml(self, content, filename):
        """
        Guarda el XML en una carpeta en el servidor.
        """

        # SET SYSTEM TIMEZONE
        os.environ['TZ'] = "America/Mexico_City"

        base_path = '%s/filestore' % config['data_dir']
        repo_path = '%s/%s' % (base_path, self._name.replace('.', '_'))
        date_path = '%s/%s' % (repo_path, date.today().isoformat()[:10])

        if not os.access(base_path, os.W_OK):
            _logger.error("No hay permisos de escritura en: %s", base_path)
            raise UserError('No hay permisos de escritura')

        self.execute('mkdir -p %s' % date_path)

        file_path = '%s/%s' % (date_path, uuid.uuid4())

        f = open(file_path, 'wb')
        f.write(content.encode())
        f.close()

        file_id = self.sudo().create({
            'name': filename,
            'path': file_path
        })

        return file_id.id

    @api.multi
    def create_invoice(self):
        """
        Esta función crea las facturas en función del xml del proveedor.
        """

        xml_text = self.xml_text.replace('xmlns:schemaLocation', 'xsi:schemaLocation')
        xml_text = xml_text.replace('<?xml version="1.0" encoding="UTF-8"?>', ' ')
        xml_text = xml_text.replace('<?xml version="1.0" encoding="utf-8"?>', ' ')
        xml_text = xml_text.replace('<?xml version="1.0" encoding="utf-8" ?>', ' ')
        xml_text = xml_text.replace('<?xml version="1.0" encoding="UTF-8" standalone="no"?>', ' ')
        xml_text = xml_text.replace('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>', ' ')

        xml_cfdi = etree.parse(StringIO(xml_text))

        quantity = ''
        unit_value = ''
        importe = ''

        account_invoice_line_ids = []
        tax_ids = []

        id_doc_xml = self.env['data.filemanager'].save_xml(self.xml_text, self.name + '.xml')

        date_formated = self.fecha_xml[2:12]

        emisor = xml_cfdi.findall('.//{http://www.sat.gob.mx/cfd/3}Emisor')
        rfc = emisor[0].get('Rfc')

        request_rfc = xml_cfdi.findall('.//{http://www.sat.gob.mx/cfd/3}Receptor')
        req_rfc = request_rfc[0].get('Rfc')

        total = self.total_xml

        order_id = self.env['purchase.order'].search([('name', '=', self.order_id.name)], limit=1)

        if order_id:

            TasaOCuota = None
            amount = None

            for item in xml_cfdi.findall('.//{http://www.sat.gob.mx/cfd/3}Concepto'):
                quantity = item.attrib['Cantidad']
                unit_value = item.attrib['ValorUnitario']
                importe = item.attrib['Importe']

                for item_tra in xml_cfdi.findall('.//{http://www.sat.gob.mx/cfd/3}Traslado'):
                    Impuesto = item_tra.attrib['Impuesto']
                    try:
                        TasaOCuota = item_tra.attrib['TasaOCuota']
                        _logger.warning("Verificando Impuesto")
                        _logger.warning(TasaOCuota)
                        amount_tax = TasaOCuota.replace("..", '.')
                        _logger.warning(amount_tax)
                        amount = float(amount_tax) * 100

                    except KeyError:
                        TasaOCuota = 0.0

                # Busca la cuenta de gastos
                acco_acco_line_id = self.env['account.account'].search(
                    [('company_id', '=', order_id.company_id.id), ('user_type_id', '=', 'Expenses')], limit=1)

                if not acco_acco_line_id:
                    order_id.sudo().message_post('No existe la cuenta de gastos para la empresa.')

                # Busca impuesto
                if amount:
                    account_tax_id = self.env['account.tax'].search(
                        [('type_tax_use', '=', 'purchase'), ('company_id', '=', order_id.company_id.id),
                         ('amount', "=", amount)], limit=1)

                    if account_tax_id:
                        # Crea linead de factura
                        account_invoice_line_ids.append((0, 0, {'name': item.attrib['Descripcion'],
                                                                'date_planned': date.now(),
                                                                'account_id': acco_acco_line_id.id,
                                                                'quantity': float(quantity),
                                                                'price_unit': float(unit_value),
                                                                'invoice_line_tax_ids': [(6, 0, [account_tax_id.id])]}))
                    else:
                        account_invoice_line_ids.append((0, 0, {'name': item.attrib['Descripcion'],
                                                                'date_planned': date.now(),
                                                                'account_id': acco_acco_line_id.id,
                                                                'quantity': float(quantity),
                                                                'price_unit': float(unit_value)}))
                        order_id.sudo().message_post('Se ha creado la factura pero no se ha encontrado los impuestos en el sistema favor de verificarlos y agregarlos manualmente.')

                else:
                    # Crea linead de factura
                    account_invoice_line_ids.append((0, 0, {'name': item.attrib['Descripcion'],
                                                            'date_planned': date.now(),
                                                            'account_id': acco_acco_line_id.id,
                                                            'quantity': float(quantity),
                                                            'price_unit': float(unit_value)}))


            currency_format = self.currency_name.replace("[", '')
            currency_format = currency_format.replace("]", '')
            currency_format = currency_format.replace("'", '')

            currency_id = self.env['res.currency'].search([('name', '=', currency_format.upper())], limit=1)

            account_journal = self.env['account.journal'].search(
                [('company_id', '=', order_id.company_id.id), ('type', '=', 'purchase'), ('currency_id', '=', currency_id.id)], limit=1)

            if not account_journal:
                self.error_name = self.error_name + ' No se tiene configurado un diario en la empresa, para poder recibir el xml.'
                order_id.sudo().message_post(
                    'No se tiene configurado un diario en la empresa, para poder recibir el xml.')
                return 0

            account_account_id = self.env['account.account'].search(
                [('company_id', '=', order_id.company_id.id), ('user_type_id', '=', 'Payable')], limit=1)

            if not account_account_id:
                _logger.critical("No tienen property_account_payable_id")
                self.error_name = self.error_name + ' No se tiene configurado la cuenta por pagar del proveedores.'
                order_id.sudo().message_post('No se tiene configurado la cuenta por pagar del proveedores.')
                return 0

            status = self.update_sat_status(rfc, req_rfc, total, self.name)

            status = 'valid'

            _logger.warning("Estatus SAT")
            _logger.warning(status)

            if not status:
                self.error_name = "El servicio de validación del SAT no funciona, inténtelo mas tarde. https://consultaqr.facturaelectronica.sat.gob.mx/"
            else:
                account_invoice_id = None

                if status == 'valid':

                    account_ids = self.env['account.invoice'].search([('reference', '=', self.name)])

                    if account_ids:
                        order_id.sudo().message_post(
                            'La factura fue creada sin especificar en el asunto la orden de compra, favor de relacionarla. :) ' + self.name)
                        raise ValidationError('Ya existe esta factura creada apartir de este XML.')



                    account_invoice_id = self.sudo().env['account.invoice'].create({
                        'partner_id': order_id.partner_id.id,
                        'origin': order_id.name,
                        'order_id': order_id.id,
                        'account_id': account_account_id.id,
                        'journal_id': account_journal.id,
                        'currency_id': currency_id.id,
                        'company_id': order_id.company_id.id,
                        'invoice_line_ids': account_invoice_line_ids,
                        'reference': self.name,
                        'doc_xml': id_doc_xml,
                        'payment_term_id': order_id.payment_term_id.id,
                        'date_invoice': date_formated,
                        'type': 'in_invoice',
                        'name': self.folio_xml,
                    })

                    _logger.warning("Por que no se crea :(")
                    _logger.warning(account_invoice_id)

                if status == 'not_found':
                    self.error_name = "La factura no funciona. No es valida ante el SAT"
                    return True

                if status == 'cancelled':
                    self.error_name = "La factura fue cancelada. Esta cancelada ante el SAT"
                    return True

                if self.error_name == '':
                    _logger.warning("#####################")
                    _logger.warning("#####################")
                    _logger.warning("#####################")
                    _logger.warning("#####################")
                    _logger.warning(account_invoice_id)
                    if account_invoice_id:
                        account_invoice_id.message_post('Se ha creado la factura.: ' + self.error_name)
                else:
                    return True

                _logger.warning("#####################")
                _logger.warning("#####################")
                _logger.warning("#####################")
                _logger.warning("#####################")

                order_id.invoice_ids = (4, account_invoice_id.id)

                self.unlink()

                return True



        else:

            # Crear factura sin orden de compra en el asunto

            TasaOCuota = None
            company_id = None
            amount = None

            for item in xml_cfdi.findall('.//{http://www.sat.gob.mx/cfd/3}Concepto'):
                quantity = item.attrib['Cantidad']
                unit_value = item.attrib['ValorUnitario']
                importe = item.attrib['Importe']

                for item_tra in xml_cfdi.findall('.//{http://www.sat.gob.mx/cfd/3}Traslado'):
                    Impuesto = item_tra.attrib['Impuesto']
                    try:
                        TasaOCuota = item_tra.attrib['TasaOCuota']
                        _logger.warning("Verificando Impuesto")
                        _logger.warning(TasaOCuota)
                        amount_tax = TasaOCuota.replace("..", '.')
                        _logger.warning(amount_tax)
                        amount = float(amount_tax) * 100

                    except KeyError:
                        TasaOCuota = 0.0

                company_id = self.env['res.company'].search([('vat', '=', self.rfc_company)], limit=1)

                # Busca la cuenta de gastos
                acco_acco_line_id = self.env['account.account'].search(
                    [('company_id', '=', company_id.id), ('user_type_id', '=', 'Expenses')], limit=1)

                if not acco_acco_line_id:
                    _logger.warning("No existe la cuenta de gastos para la empresa.")

                # Busca impuesto
                if amount:
                    account_tax_id = self.env['account.tax'].search(
                        [('type_tax_use', '=', 'purchase'), ('company_id', '=', company_id.id),
                         ('amount', "=", amount)], limit=1)

                # Crea linead de factura

                if account_tax_id:
                    account_invoice_line_ids.append((0, 0,
                                                     {'name': item.attrib['Descripcion'], 'date_planned': datetime.now(),
                                                      'account_id': acco_acco_line_id.id, 'quantity': float(quantity),
                                                      'price_unit': float(unit_value),
                                                      'invoice_line_tax_ids': [(6, 0, [account_tax_id.id])]}))
                else:
                    account_invoice_line_ids.append((0, 0,
                                                     {'name': item.attrib['Descripcion'], 'date_planned': datetime.now(),
                                                      'account_id': acco_acco_line_id.id, 'quantity': float(quantity),
                                                      'price_unit': float(unit_value)}))
                    order_id.sudo().message_post('Se ha creado la factura pero no se ha encontrado los impuestos en el sistema favor de verificarlos y agregarlos manualmente.')



            account_journal = self.env['account.journal'].search(
                [('company_id', '=', company_id.id), ('type', '=', 'purchase'), ('currency_id', '=', currency_id.id)], limit=1)

            if not account_journal:
                self.error_name = self.error_name + ' No se tiene configurado un diario en la empresa, para poder recibir el xml.'
                _logger.warning('No se tiene configurado un diario en la empresa, para poder recibir el xml.')
                return 0

            account_account_id = self.env['account.account'].search(
                [('company_id', '=', company_id.id), ('user_type_id', '=', 'Payable')], limit=1)

            if not account_account_id:
                _logger.critical("No tienen property_account_payable_id")
                self.error_name = self.error_name + ' No se tiene configurado la cuenta por pagar del proveedores.'
                _logger.warning('No se tiene configurado la cuenta por pagar del proveedores.')
                return 0

            res_partner_id = self.env['res.partner'].search([('vat', '=', self.rfc)], limit=1)

            status = self.update_sat_status(rfc, req_rfc, total, self.name)

            account_invoice_id = None

            payment_term_id = None
            if res_partner_id.property_supplier_payment_term_id:
                payment_term_id = res_partner_id.property_supplier_payment_term_id.id
            else:
                pay_term_id = self.env['account.payment.term'].search([], limit=1)
                payment_term_id = pay_term_id.id

            if status == 'valid':

                account_ids = self.env['account.invoice'].search([('reference', '=', self.name)])

                if account_ids:
                    raise ValidationError('Ya existe esta factura creada apartir de este XML.')

                account_invoice_id = self.env['account.invoice'].create({
                    'partner_id': res_partner_id.id,
                    'account_id': account_account_id.id,
                    'journal_id': account_journal.id,
                    'currency_id': currency_id.id,
                    'company_id': company_id.id,
                    'invoice_line_ids': account_invoice_line_ids,
                    'reference': self.name,
                    'doc_xml': id_doc_xml,
                    'payment_term_id': payment_term_id,
                    'date_invoice': date_formated,
                    'type': 'in_invoice',
                    'name': self.folio_xml,
                })

            if status == None:
                _logger.warning("NO hay conexion con el validador del SAT")

            if status == 'not_found':
                self.error_name = "La factura no funciona. No es valida ante el SAT"
                return True

            if status == 'cancelled':
                self.error_name = "La factura fue cancelada. Esta cancelada ante el SAT"
                return True

            if self.error_name == '':
                account_invoice_id.sudo().message_post('Se ha creado la factura.: ' + self.error_name)
            else:
                return True