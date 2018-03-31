# -*- coding: utf-8 -*-
# © <2017> <Juan Carlos Vazquez Beas (jcvazquez@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import sys, logging
from odoo import api, fields, models

reload(sys)  
sys.setdefaultencoding('utf8')
_logger = logging.getLogger(__name__)

class hr_job(models.Model):
    _name = 'hr.job'
    _inherit = ['hr.job','website.seo.metadata']

    icon = fields.Binary(
        string='Icono sitio web',
    )
    icon_filename = fields.Char(
        string='Nombre del icono',
    )
    publish_job_web = fields.Many2one(
        comodel_name='hr.publish.job.web', 
        string='Publicación de vacantes'
    )
    website_published = fields.Boolean(
        string='Publicado',
    )


    @api.multi
    def no_publish_job(self):
        _logger.warning("---------")
        _logger.warning(self.website_published)
        self.website_published = False

    @api.multi
    def publish_job(self):
        self.website_published = True

    def get_unit(self):
        if self.job_id_boss:
            empl_id = self.env['hr.job'].sudo().search([('department_id','child_of',self.department_id.id),('job_id_boss','!=',self.job_id_boss.id)])
            _logger.warning("Estos son sus hijos")
            _logger.warning(empl_id)
            return empl_id
        else:
            empl_id = self.env['hr.job'].sudo().search([('job_id_boss','=',self.id)])
            return empl_id