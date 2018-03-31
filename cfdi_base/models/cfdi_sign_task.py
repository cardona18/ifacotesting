
# -*- coding: utf-8 -*-
# © <2016> <Omar Torres Silva (otorres@grupoifaco.com.mx) >
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import base64
import hashlib
import logging
import logging
import os
import re
import subprocess
import sys
import uuid
from lxml import etree as ET
from M2Crypto import RSA
from suds import WebFault
from suds.client import Client
from types import *

from openerp import fields, models, api
from openerp.exceptions import Warning

_logger = logging.getLogger(__name__)

class CFDISignTask(models.TransientModel):
    _name = 'cfdi.sign.task'
    _description = 'CFDI SIGN TASK'

    company_id = fields.Many2one(
        string='Empresa',
        comodel_name='res.company'
    )

    __config = {}
    __ws_options = {}

    def prepare(self, _config = {}):
      """
      LOAD REQUIRED FILES AND CONFIGURATION
      """

      server_config = self.env['cfdi.server.config'].create({})
      self.__config['url'] = server_config['default_service_url']
      self.__ws_options['UserID'] = server_config['default_user']
      self.__ws_options['UserPass'] = server_config['default_password']
      self.__ws_options['emisorRFC'] = self.company_id.rfc

      for key, value in _config.iteritems():
        if key in ['emisorRFC', 'UserID', 'UserPass']:
          self.__ws_options.update({ key: value })

      if not self.company_id.cert_file or not self.company_id.key_file or not self.company_id.cert_pass:
        raise Warning('No se encontró en certificado de la empresa:\n %s' % self.company_id.name)

      base_path = '/tmp/odoo_sign/%s' % uuid.uuid4()
      self.__config['cert_file'] = '%s/tmp_file.cer' % base_path
      self.__config['key_file'] = '%s/tmp_file.key' % base_path

      self.execute("mkdir -p %s" % base_path)

      # CREATE TEMPLATE
      f = open(self.__config['cert_file'], 'wb')
      f.write(self.company_id.cert_file.decode('base64'))
      f.close()

      # CREATE TEMPLATE
      f = open(self.__config['key_file'], 'wb')
      f.write(self.company_id.key_file.decode('base64'))
      f.close()

      if os.path.isfile(self.__config['key_file']) and os.access(self.__config['key_file'], os.R_OK):
          self.execute("openssl pkcs8 -inform DER -in {0} -out {0}.pem -passin pass:{1}".format(self.__config['key_file'], self.company_id.cert_pass))

      if os.path.isfile(self.__config['cert_file']) and os.access(self.__config['cert_file'], os.R_OK):
          snum = self.execute("openssl x509 -inform DER -in {0} -noout -serial".format(self.__config['cert_file']))
          snum = snum[snum.index('=') + 1:]
          self.__config['snum'] = ''.join(part[1:] for part in re.findall('..',snum))

    def stamp_xml(self, xml):

      if not self.__config['key_file'] or not self.__config['cert_file']:
        self.prepare()

      keys = RSA.load_key('%s.pem' % self.__config['key_file'])
      cert_file = open(self.__config['cert_file'], 'r')
      cert = base64.b64encode(cert_file.read())
      xdoc = ET.fromstring(xml)

      xdoc.attrib['Certificado'] = cert
      xdoc.attrib['NoCertificado'] = self.__config['snum']

      xsl_root = ET.parse('%s/utils/xslt33/cadenaoriginal_3_3.xslt' % os.path.dirname(__file__))
      xsl = ET.XSLT(xsl_root)
      original_string = xsl(xdoc)
      digest = hashlib.new('sha256', str(original_string)).digest()
      stamp = base64.b64encode(keys.sign(digest, "sha256"))

      xdoc.attrib['Sello'] = stamp

      return '<?xml version="1.0" encoding="UTF-8"?>\n%s' % ET.tostring(xdoc, encoding='UTF-8')

    def sign_xml(self, xml, options = { 'generarCBB': False, 'generarTXT': False, 'generarPDF': False}):

      ws_response = WsResponse()

      try:

        client = Client(self.__config['url'], timeout=10)

        options['text2CFDI'] = base64.b64encode(xml)
        self.__ws_options.update(options)
        response = client.service.requestTimbrarCFDI(self.__ws_options)

        for attribute in ['xml', 'pdf', 'png', 'txt']:
          if attribute in response:
            setattr(ws_response, attribute, response[attribute])

      except WebFault, e:
        setattr(ws_response, 'error_code', e.fault.faultcode)
        setattr(ws_response, 'error', e.fault.faultstring)
        setattr(ws_response, 'request', client.last_sent())
      except Exception, e:
        setattr(ws_response, 'error_code', 'LOST_CONNECTION')
        setattr(ws_response, 'error', e.message)

      return ws_response

    def execute(self, _command):
        try:
            return subprocess.check_output(_command, shell=True, stderr=subprocess.STDOUT)
        except Exception, e:
            _logger.error('EXECUTE ERROR: %s', e)

    def prepare_ws_config(self):

      server_config = self.env['cfdi.server.config'].create({})
      self.__config['url'] = server_config['default_service_url']
      self.__ws_options['UserID'] = server_config['default_user']
      self.__ws_options['UserPass'] = server_config['default_password']
      self.__ws_options['emisorRFC'] = self.company_id.rfc

    def cfdi_cancel(self, uuid):

      ws_response = WsResponse()

      try:

        client = Client(self.__config['url'], timeout=10)

        self.__ws_options.update({'uuid': uuid})
        response = client.service.requestCancelarCFDI(self.__ws_options)
        setattr(ws_response, 'result', True)

      except WebFault, e:
        setattr(ws_response, 'error_code', e.fault.faultcode)
        setattr(ws_response, 'error', e.fault.faultstring)
        setattr(ws_response, 'request', client.last_sent())
        setattr(ws_response, 'result', False)
      except Exception, e:
        setattr(ws_response, 'error_code', 'LOST_CONNECTION')
        setattr(ws_response, 'error', e.message)
        setattr(ws_response, 'result', False)

      return ws_response

class WsResponse():
  """
  Sign server response
  """

  def has(self, _name):
    return hasattr(self, _name)