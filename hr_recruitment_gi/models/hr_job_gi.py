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

reload(sys)
sys.setdefaultencoding('utf8')
_logger = logging.getLogger(__name__)

class hr_job_gi(models.Model):
    _inherit = 'hr.job'
    _description = 'Extension de la clase hr_job para adecuaciones internas'

    def _get_my_department_job(self):
        employees = self.env.user.employee_ids

        return (employees[0].department_id if employees
            else self.env['hr.department'])

    def get_x_tem_current(self):
        for self_id in self:
            empl_id = self.env['hr.employee'].sudo().search([('job_id', '=', self_id.id),('empl_temp','=',True)])
            self_id.x_tem_current = len(empl_id)

    def get_x_num_aut_emplo_cu(self):
        for self_id in self:
            empl_id = self.env['hr.employee'].sudo().search([('job_id', '=', self_id.id),('empl_temp','=',False)])
            self_id.x_num_aut_emplo_cur = len(empl_id)

    def search_unit(self, parent_ids):
        for parent_id in parent_ids:
            if parent_id.type_department == 'unity_cate':
                return parent_id.name
            else:
                self.search_unit(parent_id.parent_id)


    name = fields.Char(
        string="Nombre del puesto", 
        size=80)
    my_department_id = fields.Many2one(
        comodel_name='hr.department', 
        string='Mi Departemento', 
        default=_get_my_department_job
    )
    department_id = fields.Many2one(
        comodel_name='hr.department', 
        string='Departemento'
    )
    x_company_id = fields.Many2one(
        comodel_name='res.company', 
        string='Empresa solicitante', 
        default=lambda self: self.env.user.company_id, 
        required=True
    )
    x_num_aut_emplo = fields.Integer(
        string='Personal fijo autorizado'
    )
    x_num_aut_emplo_cur = fields.Integer(
        string='Personal fijo actual', 
        compute=get_x_num_aut_emplo_cu
    )
    x_descrip_job = fields.Binary(
        string='Perfil y descriptivo del puesto'
    )
    x_plan_registration = fields.Binary(
        string='Plan y registro de inducción al puesto'
    )
    x_rev = fields.Char(
        string='Número de revisión', 
        size=20
    )
    x_code = fields.Char(
        string='Código del puesto', 
        size=20
    )
    x_tem_emplo = fields.Integer(
        string='Puestos temporales autorizados'
    )
    x_tem_current = fields.Integer(
        string='Puestos temporales ocupados', 
        compute=get_x_tem_current
    )
    x_start_date_temp = fields.Date(
        string='Inicio'
    )
    x_end_date_temp = fields.Date(
        string='Fin'
    )
    x_req_pro_desc = fields.Boolean(
        string='¿Es requerido?', 
        default=True, 
        help="El documento será requerido cuando se haga una requisición de personal"
    )
    x_pro_doc = fields.Binary(
        string='Perfil y descriptivo del puesto'
    )
    x_pro_doc_name = fields.Char(
        string='Nombre del Perfil y descriptivo'
    )
    x_req_plan = fields.Boolean(
        string='¿Es requerido?', 
        default=True, 
        help="El documento será requerido cuando se haga una requisición de personal"
    )
    x_plan_doc = fields.Binary(
        string='Plan y registro de inducción al puesto'
    )
    x_plan_doc_name = fields.Char(
        string='Nombre del plan'
    )
    x_req_quiz = fields.Boolean(
        string='¿Es requerido?', 
        default=False, 
        help="El documento será requerido cuando se haga una requisición de personal"
    )
    x_quiz_doc = fields.Binary(
        string='Exámenes de conocimientos del área'
    )
    x_quiz_doc_name = fields.Char(
        string='Nombre del Examen'
    )
    # configuration_hr_gi = fields.Many2one(
    #     comodel_name='configuration_hr_gi', 
    #     string='Configuración smtp'
    # )
    is_director = fields.Boolean(
        string='Puesto de director'
    )
    is_manager = fields.Boolean(
        string='Puesto de gerente'
    )
    is_boss = fields.Boolean(
        string='Puesto de jefe'
    )
    category_job = fields.Selection(
        selection=[
        ('is_director', 'Puesto de director'),
        ('is_manager', 'Puesto de gerente'),
        ('is_boss', 'Puesto de jefe'),
        ('contributor_ind', 'Contribuidor individual'),
        ('operator', 'Operador'),                                
        ], 
        string='Categoría del puesto'
    )
    job_id_boss = fields.Many2one(
        comodel_name='hr.job',
        string='Puesto padre'
    )
    no_of_employee_cur  = fields.Integer(
        string='Número total de empleados', 
        compute='_get_nbr_employees'
    )
    state = fields.Selection([('draft', 'Borrador'),
            ('create', 'Puesto creado'),
            ('open', ' '),#Este estado lo necesita odoo para su proceso por default
            ('recruit', ' '),#Este estado lo necesita odoo por default
            ('wit_vac_avai', 'Con vacantes disponibles'),
            ('wit_vac_occ', 'Vacantes completadas'),
            ('wit_vac_tem', 'Con vacantes temporales')
        ], 
        string='Estado', 
        default='draft'
    )
    old_id = fields.Integer(
        string='ID odoo 8',
    )

    @api.multi
    def _compute_application_count(self):
        for self_id in self:

            read_group_result = self.env['hr.applicant'].read_group([('job_id', '=', self_id.id)], ['job_id'], ['job_id'])
            result = dict((data['job_id'][0], data['job_id_count']) for data in read_group_result)
            for job in self_id:
                job.application_count = result.get(job.id, 0)

    @api.one
    def _get_nbr_employees(self):
        no_of_empl = self.env['hr.employee'].search([('job_id.id', '=', self.id),('active', '=', 1)])
        auxIds=[]
        for get_no_of_empl in no_of_empl:
            auxIds.append(get_no_of_empl.id)
        self.no_of_employee_cur = len(auxIds)


    @api.multi
    def create_new_job(self):
        self.state = 'create'
        template = self.env['mail.template'].search([('name', '=', 'Notify new job gi')], limit=1)

        template.send_mail(self.id, force_send=True)

        

    # @api.model
    # def create(self, values):
    #     res_id  = super(hr_job_gi, self).create(values)
    #     return res_id


    @api.multi
    def job_is_published(self):
       self.is_published = True

    @api.multi
    def job_no_published(self):
        self.is_published = False

    # @api.multi
    # def unlink(self):
    #     for self_id in self:
    #         if self_id.no_of_employee_cur > 0:
    #             raise osv.except_osv('Advertencia','No puedes eliminar este puesto por que hay empleados ocupándolo.')
    #         else:
    #             return models.Model.unlink(self_id)


    @api.onchange('x_num_aut_emplo')
    def _onchange_x_num_aut_emplo(self):
        if self.x_num_aut_emplo >= 99999:
            self.x_num_aut_emplo = 99999
            return {'value':{},'warning':{'title':'Advertencia','message':'No puedes autorizar mas de 99999 puestos'}}


    @api.onchange('x_tem_emplo')
    def _onchange_x_tem_emplo(self):
        self.x_start_date_temp = None
        self.x_end_date_temp =None
        if self.x_num_aut_emplo == self.no_of_employee_cur:
            if self.x_num_aut_emplo < self.x_tem_emplo:
                self.x_tem_emplo = self.x_num_aut_emplo
                return {'value':{},'warning':{'title':'Advertencia','message':'No puedes crear mas puestos temporales que el personal autorizado'}}


    @api.onchange('x_start_date_temp')
    def _onchange_x_start_date_temp(self):
        if self.x_end_date_temp:
            if self.x_start_date_temp > self.x_end_date_temp:
                self.x_end_date_temp = None
                return {'value':{},'warning':{'title':'Advertencia ','message':'La fecha de fin es menor a la de inicio'}}


    def hr_job_cron(self, cr, uid, context=None):
        date_tem_obj = self.pool.get('hr.job')
        date_tem_ids = self.pool.get('hr.job').search(cr, uid, [])
        for date_tem_id in date_tem_ids:
            scheduler_line =date_tem_obj.browse(cr, uid,date_tem_id ,context=context)
            job_po_start_date_temp      = scheduler_line.x_start_date_temp
            job_po_ple_them             = scheduler_line.x_end_date_temp
            if job_po_start_date_temp > job_po_ple_them:
                date_tem_obj.write(cr, uid, date_tem_id, {'x_start_date_temp': None,'x_end_date_temp': None, 'x_tem_emplo': 0}, context=context)


    # @api.multi
    # def get_dir_ids(self):
    #     directors_ids = self.env['hr.job'].search([('category_job', '=', 'is_director')])

    #     cont_dir_ids = []

    #     for directors_id in directors_ids:
    #         cont_dir_ids.append(str(directors_id.id)+'-'+directors_id.name)


    #     return cont_dir_ids


    # @api.multi
    # def get_child_ids(self):
    #     directors_ids = self.env['hr.job'].search([('category_job', '=', 'is_director')])

    #     cont_dir_ids = []
    #     child_of_dir_cont = []

    #     for directors_id in directors_ids:

    #         _logger.warning("--------------------------")
    #         _logger.warning(directors_id.name)
    #         _logger.warning(directors_id.job_id_boss)

    #         if directors_id.job_id_boss:
    #             child_of_dir = self.env['hr.job'].search([('department_id', 'child_of', directors_id.department_id.id), ('is_published', '=', True)])

    #             for child_id in child_of_dir:
    #                 child_of_dir_cont.append(str(directors_id.id)+'-'+str(child_id.id)+'-'+child_id.name)
            
    #         else:

    #             _logger.warning(directors_id.name+'No tiene jefe')
    #             child_of_dir = self.env['hr.job'].search([('job_id_boss', '=', directors_id.id), ('is_published', '=', True)])


    #             _logger.warning(child_of_dir)

    #             for child_id in child_of_dir:
    #                 child_of_dir_cont.append(str(directors_id.id)+'-'+str(child_id.id)+'-'+child_id.name)

    #             cont_dir_ids.append(str(directors_id.id)+'-'+directors_id.name)

    #     return child_of_dir_cont
