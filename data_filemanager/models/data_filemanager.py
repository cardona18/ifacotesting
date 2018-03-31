# -*- coding: utf-8 -*-
# © <2017> <Omar Torres Silva (otorresgi18@gmail.com)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime
import base64
import logging
import os
import subprocess
import uuid

from openerp import fields, models, api
from odoo.exceptions import UserError
from openerp.tools import config

_logger = logging.getLogger(__name__)

class data_filemanager(models.Model):
    _name = 'data.filemanager'
    _description = 'DATA FILEMANAGER'

    name = fields.Char(
        string='Nombre',
        required=True
    )
    path = fields.Char(
        string='Ruta',
    )

    @api.multi
    def remove_all(self):

        for item in self:

            if os.access(item.path, os.W_OK):
                os.remove(item.path)

        return super(data_filemanager, self).sudo().unlink()

    def save_base64(self, content, filename):

        # SET SYSTEM TIMEZONE
        os.environ['TZ'] = "America/Mexico_City"

        base_path = '%s/filestore' % config['data_dir']
        repo_path = '%s/%s' % (base_path, self._name.replace('.','_'))
        date_path = '%s/%s' % (repo_path,datetime.today().isoformat()[:10])

        if not os.access(base_path, os.W_OK):
            _logger.error("No hay permisos de escritura en: %s", base_path)
            raise UserError('No hay permisos de escritura')

        self.execute('mkdir -p %s' % date_path)

        file_path = '%s/%s' % (date_path, uuid.uuid4())

        f = open(file_path, 'wb')
        f.write(content.decode('base64'))
        f.close()

        file_id = self.sudo().create({
            'name': filename,
            'path': file_path
        })

        return file_id.id

    def update_base64(self, content, filename):

        if not os.access(self.path, os.W_OK):
            _logger.error("No hay permisos de escritura en: %s", self.path)
            raise UserError('No hay permisos de escritura')

        f = open(self.path, 'wb')
        f.write(content.decode('base64'))
        f.close()

        self.sudo().write({
            'name': filename
        })

        return True

    def file_read(self):

        if os.access(self.path, os.R_OK):
            file = open(self.path, "rb")
            data = file.read()
            file.close()
            return base64.b64encode(data)

        return False


    def execute(self, _command):
        try:
            return subprocess.check_output(_command, shell=True, stderr=subprocess.STDOUT)
        except Exception, e:
            _logger.error('EXECUTE ERROR: %s', e)