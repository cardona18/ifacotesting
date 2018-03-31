# -*- coding: utf-8 -*-
# © <2016> <Juan Carlos VB (jcvazquez@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
import sys  
from openerp.osv import osv
from openerp import fields, models, api

reload(sys)  
sys.setdefaultencoding('utf8')

_logger = logging.getLogger(__name__)

class hr_aprov_aplicant(models.Model):
    _name               = 'hr.aprov.aplicant'
    _description        = 'Medicina laboral'

    _sql_constraints = [
        ('aplicant_id', 'unique(aplicant_id)', 'Ya existe una solicitud para este paciente.')
    ]

    aplicant_id         = fields.Many2one('hr.applicant', 'Nombre del paciente', required="1" ,ondelete='cascade', domain="[('state', '=', 'Segunda_entrevista')]")
    name                = fields.Char(related='aplicant_id.name', string='Nombre' )      
    job_id              = fields.Many2one('hr.job', 'Nombre del puesto')
    r_comment           = fields.Text(string="Comentarios")
    r_job_id            = fields.Many2one(related='aplicant_id.job_id', string="Nombre del puesto a ocupar", readonly="1")
    r_x_pro_doc_name    = fields.Char(related='r_job_id.x_pro_doc_name', string='Nombre del archivo', readonly="1" )
    r_x_pro_doc         = fields.Binary(related='r_job_id.x_pro_doc', string="Perfil y descriptivo del puesto", readonly="1")
    r_department_id     = fields.Many2one(related='aplicant_id.department_id', string="Departamento", readonly="1")
    r_company_id        = fields.Many2one(related='aplicant_id.company_id', string="Compañia", readonly="1")

    state               = fields.Selection([('draft', 'Por validar'),
                                        ('suitable', 'Apto para el puesto'),
                                        ('no_suitable', 'No Apto para el puesto')
                                        ], string='Estado', default='draft')
    request_gi          = fields.Many2one(comodel_name='hr.employee.request')
    job_id_reque        = fields.Many2one(related='request_gi.job_id')




    @api.multi
    def suitable_emp(self):
        self.sudo().aplicant_id.state = 'Propuesta_salarial'
        stage = self.env['hr.recruitment.stage'].search([('name', '=', 'Propuesta salarial')], limit=1)
        # self.sudo().aplicant_id.stage_id = stage.id

        sql = "UPDATE hr_applicant SET stage_id="+str(stage.id)+" WHERE id="+str(self.sudo().aplicant_id.id)+";"
        self.env.cr.execute(sql)

        self.state = 'suitable'
        self.sudo().aplicant_id.comment_doc = self.r_comment


    @api.multi
    def no_suitable(self):
        self.sudo().aplicant_id.comment_doc = self.r_comment
        if self.sudo().aplicant_id.state == 'Examen_M':
            self.sudo().state = 'no_suitable'
            self.sudo().aplicant_id.archive_applicant()
        else:
            raise Warning(_('No puedes calificar como "no apto" a este paciente por que faltan etapas por completar, Para mayor información contacta al departamento de RH.'))