# -*- coding: utf-8 -*-
# © <2016> <Omar Torres Silva (otorres@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import base64
import cStringIO
import logging
import os
import subprocess
import sys
import uuid

from openerp import fields, models
from openerp.tools import config

_logger = logging.getLogger(__name__)

class ireport_report(models.Model):
    _name = 'ireport.report'
    _description = 'IREPORT REPORT'

    _sql_constraints = [
        ('unique_ireport', 'unique(code)', 'El reporte que intenta crear ya existe.')
    ]

    name = fields.Char(
        string='Nombre',
        required=True
    )
    code = fields.Char(
        string='Clave',
        required=True
    )
    template_file = fields.Binary(
        string='Plantilla'
    )
    template_filename = fields.Char(
        string='Archivo'
    )
    image_ids = fields.One2many(
        string='Imagenes',
        comodel_name='ireport.fixed.image',
        inverse_name='report_id'
    )

    parameters = {}

    def addParam(self, _index, _value):
        """
        Add report parameter
        """
        self.parameters[_index] = _value

    def setParameters(self, _parameters):
        """
        Set report parameters
        """
        self.parameters = _parameters

    def build(self):

        # CHANGE TIMEZONE
        os.environ['TZ'] = 'America/Mexico_City'

        report_path = '/tmp/odoo_ireport/%s' % uuid.uuid4()
        template = '%s/template.jrxml' % report_path
        jar_path = '%s/java/ReportBuilder.jar' % self.back_dir(os.path.realpath(__file__), 2)
        command = 'java -jar %s' % jar_path
        self.parameters['template_path'] = template
        self.parameters['db_user'] = config['db_user']
        self.parameters['db_host'] = config['db_host']
        self.parameters['db_pass'] = config['db_password']
        self.parameters['db'] = self.env.cr.dbname

        self.execute("mkdir -p %s" % report_path)

        # change the default encoding to write jrxml
        reload(sys)
        sys.setdefaultencoding('utf-8')

        # CREATE TEMPLATE
        f = open(template, 'w')
        f.write(self.template_file.decode('base64'))
        f.close()

        # WRITE FIXED IMAGES
        for image in self.image_ids:

            image_path = '%s/%s' % (report_path, image.imagename)

            f = open(image_path, 'w')
            f.write(image.image.decode('base64'))
            f.close()

            self.parameters[image.parameter] = image_path

        # ADD PARAMETERS
        for index in self.parameters:
            command += ' --%s="%s"' % (index, self.parameters[index])

        self.execute(command)
        _logger.debug('COMMAND: %s', command)

        # FLUSH PARAMETERS
        self.parameters = {}

        return report_path


    def execute(self, _command):
        try:
            return subprocess.check_output(_command, shell=True, stderr=subprocess.STDOUT)
        except Exception, e:
            _logger.error('EXECUTE ERROR: %s', e)

    def back_dir(self, _path, _positions):
        # Returns number of positions in path

        path_list = _path.strip('/').split('/')
        length = len(path_list)

        if(_positions >= length or _positions < 0):
                return ''

        for i in range(0, _positions):
                path_list.pop()

        return "/%s" % "/".join(path_list)