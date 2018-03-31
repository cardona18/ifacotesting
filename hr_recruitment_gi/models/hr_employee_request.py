# -*- coding: utf-8 -*-
# © <2016> <Juan Carlos Vazquez Beas (jcvazquez@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
import sys
from openerp import fields, models, api
from odoo.exceptions import UserError
from openerp.exceptions import ValidationError


reload(sys)
sys.setdefaultencoding('utf8')

_logger = logging.getLogger(__name__)

class hr_employee_request(models.Model):
    _name = 'hr.employee.request'
    _description = 'HR EMPLOYEE REQUEST'


    def get_my_department(self):     
        employees = self.env.user.sudo().employee_ids
        return (employees[0].sudo().department_id if employees else self.sudo().env['hr.department'])

    def get_company_id(self):     
        employees = self.env.user.sudo().employee_ids
        return (employees[0].sudo().department_id.company_id if employees else self.sudo().env['res.company'])
   
    name = fields.Char(
        string='Código'
    )
    employee_id = fields.Many2one(
        string='Empleado',
        comodel_name='hr.employee',
        default=lambda self: self._current_employee_id()
    )
    company_id = fields.Many2one(
        string='Empresa',
        comodel_name='res.company',
        default=get_company_id
    )
    job_id = fields.Many2one(
        string='Puesto',
        comodel_name='hr.job'
    )
    quantity = fields.Integer(
        string='Personal requerido',
        default=1
    )
    detail_filename = fields.Char(
        string='Perfil descriptivo (Nombre)'
    )
    is_student = fields.Boolean(
        string='Es practicante',
        default=False
    )
    project_file = fields.Binary(
        string='Proyecto'
    )
    project_filename = fields.Char(
        string='Proyecto (Nombre)'
    )
    state = fields.Selection(
        string='Estado',
        size=5,
        default='draft',
        selection=[
            ('draft', 'Borrador'),
            ('recruitment', 'En reclutamiento'),
            ('approved', 'Aprobado'),
            ('proposal', 'Propuesta'),
            ('canceled', 'Cancelado'),
            ('close', 'Cerrada'),
        ]
    )
    current_job_is  = fields.Many2one(
        comodel_name='hr.job', 
        string='Titulo de trabajo', 
        default=lambda self: self._get_my_job_id
    )
    department_id   = fields.Many2one(
        comodel_name='hr.department', 
        string='Departamento', 
        default=get_my_department
    )
    num_request = fields.Integer(
        string='Personal reclutado', 
        readonly=True
    )
    options_workpl  = fields.Selection(
        selection=[
            ('incre_workpla', 'Plaza nueva'),
            ('incre_workpla_temporary', 'Plaza temporal'),
            ('incre_rempl', 'Sustitución de personal')#Remplaso por empleado en espesifico
        ], 
        string="Tipo de requisición", 
    )
    exception = fields.Char(
        string='Excepción',
    )
    replace_id = fields.Many2one(
        'hr.employee', 
        string='Persona a quién remplaza',
        domain=['|',('active','=',False),('active','=',True)]
    )
    comment = fields.Text(
        string='Comentarios',
    )
    close_date = fields.Date(
        string='Fecha de cierre',
    )
    

    def _current_employee_id(self):

        employee = self.employee_id.search([('user_id', '=', self.env.uid)], limit=1)

        if not employee.id:
            raise ValidationError('No es posible crear solicitudes por qué no tienes un usuario asignado, contacte al departamento de Soporte técnico')

        return employee.id

    def _get_my_job_id(self):
        employees = self.env.user.employee_ids

        return (employees[0].job_id if employees
            else self.env['hr.job'])

    @api.onchange('employee_id')
    def options_employee_id(self):
        self.job_id = self.employee_id.job_id

    @api.onchange('options_workpl')
    def options_workpl_change(self):
        if self.options_workpl == 'incre_workpla':

            empl_id = self.env['hr.employee'].sudo().search([('job_id', '=', self.job_id.id),('empl_temp','=',False)])
            req_id = self.env['hr.employee.request'].sudo().search([('job_id', '=', self.job_id.id),('state','in',['recruitment','approved','proposal']),('options_workpl','=','incre_workpla')])

            quantity_req = 0
            for id_req in req_id:
                quantity_req = quantity_req + id_req.incre_workplace

            if len(empl_id) >= self.job_id.x_num_aut_emplo:
                raise ValidationError('No puedes solicitar una nueva plaza porque ya tienes todas ocupadas.')

            else:
                self.incre_workplace = self.job_id.x_num_aut_emplo - len(empl_id) - quantity_req


        if self.options_workpl == 'incre_workpla_temporary':

            empl_id = self.env['hr.employee'].sudo().search([('job_id', '=', self.job_id.id),('empl_temp','=',True)])
            req_id = self.env['hr.employee.request'].sudo().search([('job_id', '=', self.job_id.id),('state','in',['recruitment','approved','proposal']),('options_workpl','=','incre_workpla_temporary')])

            quantity_req = 0
            for id_req in req_id:
                quantity_req = quantity_req + id_req.incre_workplace



            if len(empl_id) >= self.job_id.x_tem_emplo:
                self.incre_workplace = 0
                return {'value':{},'Advertencia':{'title':'No puedes solicitar una plazas temporales porque ya tienes todas ocupadas.'}}

            else:
                self.incre_workplace = self.job_id.x_tem_emplo - len(empl_id) - quantity_req


    @api.onchange('quantity')
    def onchange_quantity(self):

        if self.options_workpl == 'incre_workpla':

            empl_id = self.env['hr.employee'].sudo().search([('job_id', '=', self.job_id.id),('empl_temp','=',False)])
            req_id = self.env['hr.employee.request'].sudo().search([('job_id', '=', self.job_id.id),('state','in',['recruitment','approved','proposal']), ('options_workpl','=','incre_workpla')])

            quantity_req = 0
            for id_req in req_id:
                quantity_req = quantity_req + id_req.quantity


            if self.quantity > self.job_id.x_num_aut_emplo - len(empl_id) - quantity_req:
                self.exception = 'Se solicitaron mas puestos de los que tienes autorizados. Tienes autorizados '+str(self.job_id.x_num_aut_emplo - len(empl_id)- quantity_req)+'.Ya tienes cubiertas todas las vacantes. Si crees que esto es incorrecto comunicate al departamento de RH'


        if self.options_workpl == 'incre_workpla_temporary':

            empl_id = self.env['hr.employee'].sudo().search([('job_id', '=', self.job_id.id),('empl_temp','=',True)])
            req_id = self.env['hr.employee.request'].sudo().search([('job_id', '=', self.job_id.id),('state','in',['recruitment','approved','proposal']), ('options_workpl','=','incre_workpla_temporary')])


            quantity_req = 0
            for id_req in req_id:
                quantity_req = quantity_req + id_req.quantity



            if self.quantity > self.job_id.x_tem_emplo - len(empl_id) - quantity_req:
                self.exception = 'Se solicitaron mas puestos de los que tienes autorizados. Tienes autorizados '+str(self.job_id.x_tem_emplo - len(empl_id) - quantity_req)+ '.Ya tienes cubiertas todas las vacantes temporales. Si crees que esto es incorrecto comunicate al departamento de RH'


    @api.multi
    def send(self):
        
        if self.replace_id:
            reques_rep = self.env['hr.employee.request'].search([('job_id', '=', self.job_id.id),('replace_id','=',self.replace_id.id),('state','not in',['canceled','draft'])])

            if reques_rep:
                raise ValidationError('Ya existe una requisición para remplazar este empleado.')



        if self.options_workpl == 'incre_workpla':

            empl_id = self.env['hr.employee'].sudo().search([('job_id', '=', self.job_id.id),('empl_temp','=',False)])
            req_id = self.env['hr.employee.request'].sudo().search([('job_id', '=', self.job_id.id),('state','in',['recruitment','approved','proposal']), ('options_workpl','=','incre_workpla')])

            quantity_req = 0
            for id_req in req_id:
                quantity_req = quantity_req + id_req.quantity

            if self.quantity > self.job_id.x_num_aut_emplo - len(empl_id) - quantity_req:
                self.exception = 'Se solicitaron mas puestos de los que tienes autorizados. Tienes autorizados '+str(self.job_id.x_num_aut_emplo - len(empl_id)- quantity_req)+'.Ya tienes cubiertas todas las vacantes. Si crees que esto es incorrecto comunicate al departamento de RH'


        if self.options_workpl == 'incre_workpla_temporary':

            empl_id = self.env['hr.employee'].sudo().search([('job_id', '=', self.job_id.id),('empl_temp','=',True)])
            req_id = self.env['hr.employee.request'].sudo().search([('job_id', '=', self.job_id.id),('state','in',['recruitment','approved','proposal']), ('options_workpl','=','incre_workpla_temporary')])

            quantity_req = 0
            for id_req in req_id:
                quantity_req = quantity_req + id_req.quantity

            if self.quantity > self.job_id.x_tem_emplo - len(empl_id) - quantity_req:
                self.exception = 'Se solicitaron mas puestos de los que tienes autorizados. Tienes autorizados '+str(self.job_id.x_tem_emplo - len(empl_id) - quantity_req)+ '.Ya tienes cubiertas todas las vacantes temporales. Si crees que esto es incorrecto comunicate al departamento de RH'

        self.state = 'recruitment'

    @api.multi
    def canceled(self):
        self.state = 'canceled'


    @api.multi
    def progress(self):
        self.state = 'progress'

        if(self.job_id.state == 'recruit'):
            return

        return self.job_id.set_recruit()

    @api.multi
    def close_request(self):
        self.close_date = fields.Date.today()
        self.state = "close"


    @api.onchange('job_id')
    def _check_documents_required(self):

        if self.job_id:

            _logger.warning("self.department_id")
            _logger.warning(self.job_id.department_id)
            self.department_id = self.job_id.department_id.id

            documents_missing = []
            if self.job_id.x_req_pro_desc:
                if self.job_id.x_pro_doc == None:
                    documents_missing.append('Perfil y descriptivo del puesto, ')
            if self.job_id.x_req_plan:
                if self.job_id.x_plan_doc == None:
                    documents_missing.append('Plan y registro de inducción al puesto, ')
            if self.job_id.x_req_quiz:
                if self.job_id.x_quiz_doc == None:
                    documents_missing.append('Exámene de conocimientos, ')
            document = ''.join(documents_missing)
            if len(documents_missing)!=0:
                self.job_id = None
                raise ValidationError('Advertencia ¡Puesto de trabajo sin documentación completa! '+document+' Los documentos anteriores son requeridos para hacer la requisición de personal para mayor información consulta al departamento de recursos humanos')

    @api.model
    def create(self, vals):

        rec = super(hr_employee_request, self).create(vals)

        if int(vals['quantity']) <= 0:
            raise ValidationError('Tu solicitud no debe de ser menor de 1')


        rec.sudo().write({
            'name': 'REQ-%s' % str(rec.id).zfill(6)
        })

        return rec
