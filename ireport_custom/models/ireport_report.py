# -*- coding: utf-8 -*-
# © <2016> <Omar Torres Silva (otorres@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from urllib.parse import quote
import base64
import locale
import logging
import os
import subprocess
import sys
import uuid

from odoo import fields, models, api
from odoo.tools import config

_logger = logging.getLogger(__name__)

class ireport_report(models.Model):
    _name = 'ireport.report'
    _description = 'IREPORT REPORT'

    _sql_constraints = [
        ('unique_ireport', 'unique(code)', 'El reporte que intenta crear ya existe.')
    ]

    name = fields.Char(
        string='Nombre',
        required=True,
        translate=True
    )
    code = fields.Char(
        string='Clave',
        required=True
    )
    model_name = fields.Char(
        string='Modelo'
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

        # SET SYSTEM LOCALE
        locale.setlocale(locale.LC_ALL, 'es_MX.UTF-8')

        report_path = '/tmp/odoo_ireport/%s' % uuid.uuid4()
        template = '%s/template.jrxml' % report_path
        jar_path = '%s/java/ReportBuilder.jar' % self.back_dir(os.path.realpath(__file__), 2)
        command = 'java -jar %s' % jar_path
        self.parameters['template_path'] = template
        self.parameters['db_user'] = config['db_user']
        self.parameters['db_host'] = config['db_host']
        self.parameters['db_pass'] = config['db_password']
        self.parameters['db'] = self.env.cr.dbname
        self.parameters['db_port'] = config['db_port']

        #self.execute("mkdir -p %s" % report_path)

        try:
            # Create target Directory
            os.mkdir(report_path)
            _logger.info("Directory ", report_path, " Created ")
        except FileExistsError:
            _logger.info("Directory ", report_path, " already exists")

        # CREATE TEMPLATE
        f = open(template, 'wb')
        f.write(base64.decodebytes(self.template_file))
        f.close()

        # WRITE FIXED IMAGES
        for image in self.image_ids:

            image_path = '%s/%s' % (report_path, image.imagename)

            f = open(image_path, 'wb')
            f.write(base64.decodebytes(image.image))
            f.close()

            self.parameters[image.parameter] = image_path

        # ADD PARAMETERS
        for index in self.parameters:
            command += ' --%s="%s"' % (index, self.parameters[index])

        self.execute(command)
        _logger.info('COMMAND: %s', command)

        # FLUSH PARAMETERS
        self.parameters = {}

        return report_path


    def execute(self, _command):
        try:
            return subprocess.check_output(_command, shell=True, stderr=subprocess.STDOUT)
        except Exception as e:
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

    @api.multi
    def check_print_templates(self, current_model):

        templates = self.sudo().search_read([('model_name', '=', current_model)])

        return [
            {
                'id': self.env.ref('ireport_custom.print_ireport_templates').id
            },
            templates
        ]

    @api.multi
    def print_from_menu(self):

        report = self.browse(self.env.context.get('active_id', False))
        out_name = report.code

        parameters = {
            'ids': ','.join( str(inv_id) for inv_id in self.env.context.get('active_ids', []) ),
            'out_name': out_name
        }

        report.setParameters(parameters)

        report_file  = report.build()
        report_file += '/%s.pdf' % out_name

        return {
            'type' : 'ir.actions.act_url',
            'url': '/web/ireport/download_manager?path=%s&type=%s' % (quote(report_file), 'pdf'),
            'target': 'new'
        }