# -*- coding: utf-8 -*-
# © <2017> <Juan Carlos VB (jcvazquez@gmail.com)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from openerp.osv import osv
from openerp import fields, models, api

_logger = logging.getLogger(__name__)

class hr_job_org(models.Model):
    _inherit        = 'hr.job'

    org_ok = fields.Boolean(
        string='No considerar en organigrama',
    )


    @api.onchange('job_id_boss')
    def onchange_job_id_boss(self):
        if self.job_id_boss:
            _logger.warning("------------------------")
            _logger.warning(self.job_id_boss.name)
            _logger.warning(self.name)
            if self.job_id_boss.name == self.name:
                self.job_id_boss = False
                return {'value':{},'warning':{'title':'Advertencia','message':'No se debe asociar un puesto así mismo.'}}
