# -*- coding: utf-8 -*-
# © <2016> <Juan Carlos Vazquez Beas (jcvazquez@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import locale
import logging
import sys
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime
from dateutil import tz
from openerp import models, fields, api
from openerp import SUPERUSER_ID
from openerp import tools
from openerp.modules.module import get_module_resource
from openerp import models, fields,api
from openerp.osv import osv
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.exceptions import UserError
from openerp.exceptions import ValidationError

reload(sys)
sys.setdefaultencoding('utf8')

_logger = logging.getLogger(__name__)

class hr_applicant_gi(models.Model):
    _inherit        = 'hr.applicant'
    _description    = 'Extensión de la clase hr_applicant para adecuaciones internas'

    def _get_my_department_job(self):
        employees = self.env.user.employee_ids
        return (employees[0].department_id if employees
            else self.env['hr.department'])


    name = fields.Char(
        string="Nombre del solicitante"
    )
    request_emp_id = fields.Many2one(
        comodel_name='hr.employee.request',
        string='Requisicíon asociada',
    )
    partner_mobile = fields.Char(
        string="Celular", 
        required="1"
    )
    comment_fir = fields.Text(
        string="Comentario primera entrevista"
    )
    comment_sec = fields.Text(
        string="Comentario segunda entrevista"
    )
    comment_thi = fields.Text(
        string="Comentario propuesta salarial"
    )
    comment_doc = fields.Text(
        string="Comentario medicina laboral"
    )
    state = fields.Selection(
        selection=[
            ('Preselección', 'Preselección'),
            ('Primera_entrevista', 'Primera entrevista'),
            ('Segunda_entrevista', 'Segunda entrevista'),
            ('Examen_M', 'Examen médico'),
            ('Propuesta_salarial', 'Propuesta salarial'),
            ('Incorporacion', 'Incorporación'),
            # ('Descarte', 'Descarte')
        ], 
        string='Estado', 
        default='Preselección'
    )
    job_id = fields.Many2one(
        comodel_name='hr.job', 
        string='Trabajo solicitado'
    )
    company_id = fields.Many2one(
        related='job_id.x_company_id', 
        string='Compañia',
        store=True
    )
    my_depart_id = fields.Many2one(
        comodel_name='hr.department', 
        string='Mi Departemento', 
        default=_get_my_department_job
    )
    job_id_res_sel = fields.Many2one(
        comodel_name='hr.job', 
        string='Responsable de la seleccion'
    )
    res_sel_empl = fields.Many2one(
        comodel_name='hr.employee', 
        string='Nombre del Responsable'
    )
    salary_current = fields.Integer(
        string='Sueldo Actual y/o esperado'
    )
    salary_old = fields.Integer(
        string='Sueldo anterior trabajo'
    )

    def reset_applicant_gi(self):
        _logger.warning(self.state)
        self.reset_applicant()
        stage = self.env['hr.recruitment.stage'].search([('name', '=', dict(self._fields['state'].selection).get(self.state))], limit=1)

      
        if stage:
            sql = "UPDATE hr_applicant SET stage_id="+str(stage.id)+" WHERE id="+str(self.id)+";"
            self.env.cr.execute(sql)


    @api.onchange('request_emp_id')
    def onchange_request_emp_id(self):
        self.job_id = self.request_emp_id.job_id

    def onchenge_job(self):
        self.job_id = self.request_emp_id.job_id
    def onchenge_department_id(self):
        self.job_id = self.request_emp_id.job_id


    @api.one
    def action_assign(self):
        self.employee_message_follower_ids =[(6,0,self.assigned_to_id.ids)]

    def reques_data(self, cr, uid, ids, context=None):
        date_tem_obj = self.pool.get('hr.employee.request')
        date_tem_ids = self.pool.get('hr.employee.request').search(cr, uid, [])
        reques_aco = []
        for date_tem_id in date_tem_ids:
            request_gi = date_tem_obj.browse(cr, uid,date_tem_id ,context=context)
            reques_aco.append(request_gi)
        return(reques_aco)

    @api.onchange('partner_name')
    def _onchange_x_start_date_temp(self):
        self.partner_name = self.name

    @api.multi
    def Primera_entrevista(self):
        self.state = 'Primera_entrevista'
        stage = self.env['hr.recruitment.stage'].search([('name', '=', 'Primera entrevista')], limit=1)
        self.stage_id = stage.id
        self.partner_name = self.name

    @api.multi
    def Segunda_entrevista(self):
        self.state = 'Segunda_entrevista'
        stage = self.env['hr.recruitment.stage'].search([('name', '=', 'Segunda entrevista')], limit=1)
        self.stage_id = stage.id

    @api.multi
    def Propuesta_salarial(self):
        self.request_emp_id.state = 'proposal'

        self.state = 'Propuesta_salarial'
        stage = self.env['hr.recruitment.stage'].search([('name', '=', 'Propuesta salarial')], limit=1)
        self.stage_id = stage.id

    @api.multi
    def Examen_M(self):
        _logger.warning("Que demonios")
        if self.sudo().request_emp_id:
            if self.request_emp_id.state:
                self.request_emp_id.state = 'approved'

            self.state = 'Examen_M'
            stage = self.env['hr.recruitment.stage'].search([('name', '=', 'Examen médico')], limit=1)

            id_order_line = self.env['hr.aprov.aplicant'].create({
                 'aplicant_id': self.id,
            })

            self.stage_id = stage.id

            template = self.env['mail.template'].search([('name', '=', 'New patient')], limit=1)

            template.send_mail(self.id, force_send=True)
        else:
            raise ValidationError('No existe una requisición de personal asociada')



    @api.multi
    def Incorporacion(self):
        _logger.warning("#####################################")
        _logger.warning("#####################################")
        _logger.warning("#######---Incorporacion---###########")
        _logger.warning("#####################################")
        _logger.warning("#####################################")
        self.partner_name = self.name
        stage_req = self.env['hr.employee.request'].search([('job_id', '=', self.job_id.id)], limit=1)

        if self.sudo().request_emp_id:
            self.sudo().request_emp_id.state = 'proposal'
        else:
            raise osv.except_osv('Advertencia','No existe una solicitud para esta vacante.')

        self.sudo().request_emp_id.num_request = self.sudo().request_emp_id.num_request + 1
        if self.request_emp_id.num_request >= self.request_emp_id.quantity:
            self.request_emp_id.close_date = fields.Date.today()
            self.request_emp_id.state = 'close'
        else:
            self.request_emp_id.state = 'recruitment'

        self.state = 'Incorporacion'
        if not self.emp_id:
            self.create_employee_from_applicant()
        stage = self.env['hr.recruitment.stage'].search([('name', '=', 'Incorporación')], limit=1)
        self.stage_id = stage.id


    @api.multi
    def Descarte(self):
        self.state = 'Descarte'
        stage = self.env['hr.recruitment.stage'].search([('name', '=', 'Descarte')], limit=1)
        self.stage_id = stage.id

    @api.onchange('job_id')
    def onchenge_department_id(self):
        _logger.warning(self.job_id.company_id)
        self.company_id = self.job_id.company_id

    @api.multi
    def write(self,vals):
        res = super(hr_applicant_gi, self).write(vals)
        try:
            if vals['stage_id']:
                qty_steps = self.stage_id.sequence - self.last_stage_id.sequence
                if qty_steps > 1:
                    raise ValidationError('Debes de pasar por todas las etapas de una en una.')

                if self.last_stage_id.sequence > self.stage_id.sequence:

                    raise ValidationError('No puedes retroceder de etapa.')

                _logger.warning(self.stage_id.name)
                if self.stage_id.name == "Preselección":
                    self.partner_name = self.name
                    self.state = 'Preselección' 

                if self.stage_id.name == "Primera entrevista":
                    self.partner_name = self.name
                    self.state = 'Primera_entrevista'

                if self.stage_id.name == "Segunda entrevista":
                    self.partner_name = self.name
                    self.state = 'Segunda_entrevista'

                if self.stage_id.name == "Examen médico":

                    apro_apl = self.env['hr.aprov.aplicant'].search([('aplicant_id', '=', self.id)], limit=1)
                    _logger.warning("Hola")

                    if apro_apl == False:

                        if self.sudo().request_emp_id:
                            if self.request_emp_id.state:
                                self.request_emp_id.state = 'approved'

                            self.partner_name = self.name
                            self.state = 'Examen_M'


                            id_order_line = self.env['hr.aprov.aplicant'].create({
                                 'aplicant_id': self.id,
                            })

                            template = self.env['mail.template'].search([('name', '=', 'New patient')], limit=1)

                            template.send_mail(self.id, force_send=True)
                        else:
                            raise ValidationError('No existe una requisición de personal asociada')


                if self.stage_id.name == "Propuesta salarial":
                    self.partner_name = self.name
                    raise ValidationError('Debe de ser aprobado por medicina laboral para proseguir con la incorporación')

                if self.stage_id.name == "Incorporación":
                    self.partner_name = self.name
                    if not self.emp_id:
                        self.create_employee_from_applicant()
                    self.state = 'Incorporacion'

                vals['name'] = self.stage_id.name 
                return res

        except KeyError:
             return res





    @api.model
    def create(self, vals):
        rec = super(hr_applicant_gi, self).create(vals)

        return rec
