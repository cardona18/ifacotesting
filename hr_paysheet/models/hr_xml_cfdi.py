# -*- coding: utf-8 -*-
# © <2016> <Omar Torres Silva (otorres@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from lxml import etree as ET
import base64
import os
import subprocess
import sys
import urllib
import uuid

from odoo import fields, models, api
from num2words import Numero_a_Texto

import logging

_logger = logging.getLogger(__name__)

class hr_xml_cfdi(models.Model):
    _name = 'hr.xml.cfdi'
    _description = 'HR XML CFDI'

    name = fields.Char(
        string='UUID',
        size=50
    )
    send_date = fields.Datetime(
        string='Emisión'
    )
    cert_date = fields.Datetime(
        string='Certificación'
    )
    amount = fields.Float(
        string='Total'
    )
    from_date = fields.Date(
        string='Desde'
    )
    to_date = fields.Date(
        string='Hasta'
    )
    payment_date = fields.Date(
        string='Fecha pago'
    )
    rfc_src = fields.Char(
        string='Emisor',
        size=15
    )
    rfc_dst = fields.Char(
        string='Receptor',
        size=15
    )
    file_id = fields.Many2one(
        string='XML',
        comodel_name='data.filemanager'
    )
    paysheet_id = fields.Many2one(
        string='Nómina',
        comodel_name='hr.paysheet',
        ondelete='cascade'
    )
    employee_id = fields.Many2one(
        string='Empleado',
        comodel_name='hr.employee',
        related='paysheet_id.employee_id'
    )
    lot_id = fields.Many2one(
        string='Lote',
        comodel_name='hr.paysheet.lot',
        related='paysheet_id.lot_id'
    )
    paysheet_date = fields.Date(
        string='Fecha',
        related='lot_id.payment_date'
    )
    state = fields.Selection(
        string='Estado',
        default='generated',
        size=10,
        selection=[
            ('generated', 'Generado'),
            ('signed', 'Timbrado'),
            ('canceled', 'Cancelado')
        ]
    )

    @api.multi
    def unlink(self):

        for item in self:
            item.file_id.remove_all()

        return super(hr_xml_cfdi, self).unlink()

    def parse_xml(self, parse = True):

        """
        Convert xml file to object
        """

        return ET.fromstring(base64.b64decode(self.file_id.file_read())) if parse else base64.b64decode(self.file_id.file_read())

    def num2text(self, num):

        return Numero_a_Texto(num)

    @api.multi
    def export_xml_files(self):

        # SET SYSTEM TIMEZONE
        os.environ['TZ'] = "America/Mexico_City"

        base_path = '/tmp/odoo_xml/%s' % uuid.uuid4()
        zip_file  = '/tmp/odoo_xml_%s.zip' % uuid.uuid4()

        self.execute('mkdir -p %s' % base_path)

        for xml in self:

            file_path = '%s/%s' % (base_path, xml.file_id.name)

            f = open(file_path, 'wb')
            f.write(base64.b64decode(xml.file_id.file_read()))
            f.close()

        # self.execute('cd %s' % base_path)
        self.execute('zip -r -j %s %s/*' % (zip_file, base_path))
        self.execute('rm -rf %s' % base_path)

        return {
            'type' : 'ir.actions.act_url',
            'url': '/web/binary/zip_file_download?path=%s' % urllib.quote_plus(zip_file),
            'target': 'new'
        }

    def execute(self, _command):
        try:
            return subprocess.check_output(_command, shell=True, stderr=subprocess.STDOUT)
        except Exception, e:
            _logger.error('EXECUTE ERROR: %s', e)