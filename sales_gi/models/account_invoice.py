# -*- coding: utf-8 -*-
# © <2016> <Omar Torres Silva (otorres@grupoifaco.com.mx) >
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime, date, time, timedelta
from io import BytesIO
from os.path import splitext
from lxml import etree
from urllib.parse import quote
import base64
import logging
import subprocess
import tempfile
import uuid

from odoo import fields, models, api, _
from odoo.tools import DEFAULT_SERVER_TIME_FORMAT
from odoo.tools.xml_utils import _check_with_xsd

#from odoo.addons.l10n_mx_edi.models.account_invoice import CFDI_TEMPLATE
from odoo.addons.l10n_mx_edi.models.account_invoice import CFDI_TEMPLATE_33
from odoo.addons.l10n_mx_edi.models.account_invoice import CFDI_XSLT_CADENA
from odoo.addons.l10n_mx_edi.models.account_invoice import create_list_html

SHIPMENT_CFDI_33 = 'sales_gi.shipment_cfdi'

_logger = logging.getLogger(__name__)

class account_invoice_gi(models.Model):
    _inherit = 'account.invoice'

    shipment_invoice = fields.Boolean(
        string='Traslado de mercancía'
    )
    delivery_date = fields.Date(
        string='Fecha de entrega',
        track_visibility='onchenge'
    )


    @api.onchange('delivery_date')
    def onchange_delivery_date(self):
        _logger.warning("Cambiando fecha")
        if self.delivery_date:
            if self.payment_term_id:

                try:
                    date_acc = str(self.delivery_date).split('-')

                    date_f = datetime(int(date_acc[0]), int(date_acc[1]), int(date_acc[2]))

                    date_formated = date_f + timedelta(days=int(self.payment_term_id.name))

                    self.date_due = date_formated


                except Exception: 

                    self.date_due = self.delivery_date


    @api.multi
    def _l10n_mx_edi_create_cfdi(self):
        '''Creates and returns a dictionnary containing 'cfdi' if the cfdi is well created, 'error' otherwise.
        '''
        self.ensure_one()
        qweb = self.env['ir.qweb']
        error_log = []
        company_id = self.company_id
        pac_name = company_id.l10n_mx_edi_pac
        values = self._l10n_mx_edi_create_cfdi_values()

        # -----------------------
        # Check the configuration
        # -----------------------
        # -Check certificate
        certificate_ids = company_id.l10n_mx_edi_certificate_ids
        certificate_id = certificate_ids.sudo().get_valid_certificate()
        if not certificate_id:
            error_log.append(_('No valid certificate found'))

        # -Check PAC
        if pac_name:
            pac_test_env = company_id.l10n_mx_edi_pac_test_env
            pac_username = company_id.l10n_mx_edi_pac_username
            pac_password = company_id.l10n_mx_edi_pac_password
            if not pac_test_env and not (pac_username and pac_password):
                error_log.append(_('No PAC credentials specified.'))
        else:
            error_log.append(_('No PAC specified.'))

        if error_log:
            return {'error': _('Please check your configuration: ') + create_list_html(error_log)}

        # -Compute date and time of the invoice
        time_invoice = datetime.strptime(
            self.l10n_mx_edi_time_invoice, DEFAULT_SERVER_TIME_FORMAT).time()
        # -----------------------
        # Create the EDI document
        # -----------------------
        version = self.l10n_mx_edi_get_pac_version()

        # -Compute certificate data
        values['date'] = datetime.combine(
            fields.Datetime.from_string(self.date_invoice), time_invoice).strftime('%Y-%m-%dT%H:%M:%S')
        values['certificate_number'] = certificate_id.serial_number
        values['certificate'] = certificate_id.sudo().get_data()[0]

        # -Compute cfdi
        if version == '3.2':
            cfdi = qweb.render(CFDI_TEMPLATE, values=values)
            node_sello = 'sello'
            with tools.file_open('l10n_mx_edi/data/%s/cfdi.xsd' % version, 'rb') as xsd:
                xsd_datas = xsd.read()
        elif version == '3.3':
            cfdi = qweb.render(SHIPMENT_CFDI_33 if self.shipment_invoice else CFDI_TEMPLATE_33, values=values)
            node_sello = 'Sello'
            attachment = self.env.ref('l10n_mx_edi.xsd_cached_cfdv33_xsd', False)
            xsd_datas = base64.b64decode(attachment.datas) if attachment else b''
        else:
            return {'error': _('Unsupported version %s') % version}

        # -Compute cadena
        tree = self.l10n_mx_edi_get_xml_etree(cfdi)
        cadena = self.l10n_mx_edi_generate_cadena(CFDI_XSLT_CADENA % version, tree)
        tree.attrib[node_sello] = certificate_id.sudo().get_encrypted_cadena(cadena)

        # Check with xsd
        if xsd_datas:
            try:
                with BytesIO(xsd_datas) as xsd:
                    _check_with_xsd(tree, xsd)
            except (IOError, ValueError):
                _logger.info(
                    _('The xsd file to validate the XML structure was not found'))
            except Exception as e:
                return {'error': (_('The cfdi generated is not valid') +
                                    create_list_html(str(e).split('\\n')))}

        return {'cfdi': etree.tostring(tree, pretty_print=True, xml_declaration=True, encoding='UTF-8')}

    @api.multi
    def cancel_shipment_invoice(self):

        for inv in self:
            inv.state = 'open'
            inv.action_invoice_cancel()

    @api.multi
    def action_download_invoice_files(self):
        """
        Compress as ZIP file PDF and XML for selected invoices
        with customer filename format and download it
        """

        with tempfile.TemporaryDirectory() as tmpdir:

            for inv in self.filtered(lambda r: r.l10n_mx_edi_cfdi_uuid):

                zip_file = '/tmp/%s.zip' % uuid.uuid4()
                filename = splitext(inv.l10n_mx_edi_cfdi_name)[0]
                files = []

                if inv.partner_id.download_format:

                    xml = inv.l10n_mx_edi_get_xml_etree()
                    filename = inv.partner_id.download_format

                    REPLACE_VALUES = {
                        'rfc_emisor': inv.l10n_mx_edi_cfdi_supplier_rfc,
                        'rfc_receptor': inv.l10n_mx_edi_cfdi_customer_rfc,
                        'folio_odoo': str(xml.get('Folio')).zfill(4),
                        'folio_siagi': str(inv.origin[6:]).zfill(4)
                    }

                    for key, value in REPLACE_VALUES.items():
                        filename = filename.replace(key, value)

                filepath = '%s/%s' % (tmpdir, filename)
                pdf_files = self.env['ir.attachment'].search([
                    ('res_id', '=', inv.id),
                    ('res_model', '=', inv._name)
                ]).filtered(lambda r: r.datas_fname.split(".")[-1] == 'pdf')

                if len(pdf_files):

                    files.append([
                        '%s.pdf' % filepath,
                        pdf_files[0].db_datas or pdf_files[0].datas
                    ])

                files.append([
                    '%s.xml' % filepath,
                    inv.l10n_mx_edi_cfdi
                ])

                for file in files:

                    f = open(file[0], 'wb')
                    f.write(base64.b64decode(file[1]))
                    f.close()

            self.execute('zip -r -j %s %s/*' % (zip_file, tmpdir))

            return {
                'type' : 'ir.actions.act_url',
                'url': '/web/files/download?path=%s' % quote(zip_file),
                'target': 'new'
            }



    def execute(self, _command):
        """
        Execute shell command and return stdout
        """

        try:
            return subprocess.check_output(_command, shell=True, stderr=subprocess.STDOUT)
        except Exception as e:
            _logger.error('EXECUTE ERROR: %s', e)