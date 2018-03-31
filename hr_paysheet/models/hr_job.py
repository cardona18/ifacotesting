# -*- coding: utf-8 -*-
# © <2016> <Omar Torres Silva (otorres@grupoifaco.com.mx) >
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import re
import sys
import logging

from openerp import fields, models, api
from openerp.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class hr_job_gi(models.Model):
    _inherit = 'hr.job'

    @api.onchange('name')
    def _change_name(self):

        # SET DEAFULT ENCODING AS UTF-8
        reload(sys)
        sys.setdefaultencoding('utf-8')

        if self.name:

            name_re = re.compile(r"^[^\.\(\)#]{1,100}$")

            if not name_re.match(self.name):
                raise ValidationError("El nombre de puesto no puede cumple con el patrón: [.()#]{1,100}")