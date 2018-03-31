# -*- coding: utf-8 -*-

# 1 : imports of python lib
import locale
import logging
import sys  
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime, date
from dateutil import tz
import time
# 2 :  imports of openerp
from openerp import models, fields, api
from openerp import SUPERUSER_ID
from openerp import tools
from openerp.modules.module import get_module_resource
from openerp import models, fields,api
from openerp.osv import osv
#from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

reload(sys)  
sys.setdefaultencoding('utf8')

_logger = logging.getLogger(__name__)

class hr_evaluation_360(models.Model):
    _name       = 'hr.evaluation.360'

    def get_data_time(self):
        current_date = self._utc_to_tz(datetime.now(), "America/Mexico_City")
        current_date = str(current_date.isoformat())[:19]
        print(current_date)
        return (current_date)

    def _utc_to_tz(self, _date, _time_zone):
        # CONVER TO UTC
        _date = _date.replace(tzinfo = tz.gettz('UTC'))
        # LOAD TIMEZONE
        to_zone  = tz.gettz(_time_zone)
        return _date.astimezone(to_zone)


    def get_average_competitions(self):
        for self_id in self:
            cont_states = 0
            for states_ids_id in self_id.states_ids:
                if states_ids_id.state == 'yes_requ':
                    cont_states = cont_states + 1

            if cont_states == len(self_id.states_ids):
                points = 0
                cont_answ = 0
                for states_ids_id in self_id.states_ids:
                    answers = self.env['admin.answers'].search([('id_excute_plan','=',self_id.id),('is_general','=',0),('employee_evaluator','=',states_ids_id.evaluators_id.id)])
                    # _logger.warning(answers)
                    for answers_id in answers:

                        if answers_id.name == 'sel_1':
                            points = points + 100
                        if answers_id.name == 'sel_2':
                            points = points + 75
                        if answers_id.name == 'sel_3':
                            points = points + 50
                        if answers_id.name == 'sel_4':
                            points = points + 25
                        if answers_id.name == 'sel_5':
                            points = points + 0
                        if answers_id.name == 'si':
                            points = points + 100
                        if answers_id.name == 'no':
                            points = points + 0
                        if answers_id.name.isdigit():
                            points = points + float(answers_id.name)

                    cont_answ = cont_answ + len(answers)

                #Get questions general

                points_per = 0.0
                cont_points_per = 0
                points_pot = 0.0
                cont_points_pot = 0
                aco_performance = []
                aco_potential = []

                for states_ids_id in self_id.states_ids:
                    answers_gen = self.env['admin.answers'].search([('id_excute_plan','=',self_id.id),('is_general','=',1),('employee_evaluator','=',states_ids_id.evaluators_id.id)])
                    # _logger.warning(answers)
                    for answers_gen_id in answers_gen:
    

                        if answers_gen_id.general_type == 'performance':
                            if answers_gen_id.name == 'sel_1':
                                points_per = points_per + 100
                            if answers_gen_id.name == 'sel_2':
                                points_per = points_per + 75
                            if answers_gen_id.name == 'sel_3':
                                points_per = points_per + 50
                            if answers_gen_id.name == 'sel_4':
                                points_per = points_per + 25
                            if answers_gen_id.name == 'sel_5':
                                points_per = points_per + 0
                            if answers_gen_id.name == 'si':
                                points_per = points_per + 100
                            if answers_gen_id.name == 'no':
                                points_per = points_per + 0
                            if answers_gen_id.name.isdigit():
                                points_per = points_per + float(answers_gen_id.name)
                        
                            cont_points_per = cont_points_per + 1

                            aco_performance.append(answers_gen_id)

                        if answers_gen_id.general_type == 'potential':
                            if answers_gen_id.name == 'sel_1':
                                points_pot = points_pot + 100
                            if answers_gen_id.name == 'sel_2':
                                points_pot = points_pot + 75
                            if answers_gen_id.name == 'sel_3':
                                points_pot = points_pot + 50
                            if answers_gen_id.name == 'sel_4':
                                points_pot = points_pot + 25
                            if answers_gen_id.name == 'sel_5':
                                points_pot = points_pot + 0
                            if answers_gen_id.name == 'si':
                                points_pot = points_pot + 100
                            if answers_gen_id.name == 'no':
                                points_pot = points_pot + 0
                            if answers_gen_id.name.isdigit():
                                points_pot = points_pot + float(answers_gen_id.name)
                            
                            # _logger.warning(points_pot)
                            cont_points_pot = cont_points_pot + 1
                    
                        aco_potential.append(answers_gen_id)




                self_id.performance = " "
                self_id.aco_potential = " "

                if cont_points_per:
                    self_id.performance = (points_per/cont_points_per/10)
                else:
                    self_id.performance = (points_per/10)

                if cont_points_pot: 

                    self_id.potential = points_pot/cont_points_pot/10

                else:
                    self_id.potential = (points_pot/10) 


                if points:
                    self_id.competitions = format((points/cont_answ/10),'.2f')



            else:
                self_id.competitions = "Sin definir"
                self_id.performance = "Sin definir"
                self_id.potential = "Sin definir"

    def check_config(self):
        self.get_current_state()
        for self_id in self:
            cont_states = 0
            no_repit = 0
            for states_ids_id in self_id.states_ids:
                name_evaluators_id = []
                for states_ids_id in self_id.states_ids:
                    name_evaluators_id.append(states_ids_id.evaluators_id.name)
                
                for name_id in name_evaluators_id:
                    cont_names = name_evaluators_id.count(name_id)
                    if cont_names > 1:
                        no_repit = no_repit + 1

            if no_repit == 0:
                self_id.status_eval = True
                # _logger.warning(states_ids_id.evaluators_id.name)
            else:
                self_id.status_eval = False


            if len(self_id.states_ids) == 1:
                self_id.status_eval = False


    def get_exeption(self):
        return "No se pueden repetir los evaluadores en un mismo plan y debe de haber mas de un evaluador."

    start_plan  = fields.Char(
        string='Fecha de ejecución', 
        readonly=True
    )
    id_excute_plan = fields.Integer(
        string='Numero de plan',
        readonly=True, 
    )
    old_id_excute_plan = fields.Integer(
        string='Numero de plan odoo 8',
        readonly=True, 
    )

    start_eval = fields.Date(
        string='Inicio',
        required=True,
    )
    end_eval = fields.Date(
        string='Fin',
        required=True,
    )

    name        = fields.Many2one(
        'hr.plan.evaluation',
        string='Plan de evaluación',
        required=True,
        select=True,
    )
    
    evaluated_id    = fields.Many2one(
        related='name.evaluated',
        string='Nombre del puesto a evaluar',
        required=True,
    )

    department_id   = fields.Many2one(
        related='evaluated_id.department_id',
        string='Departamento del evaluado',
        required=True,
    )

    name_evaluated  = fields.Many2one(
        comodel_name='hr.employee',
        string='Nombre del empleado a evaluar',
        required=True,
        domain=['|',('active','=',True),('active','=',False)]
    )

    states_ids = fields.One2many(
        string='Tabla de evaluadores y estatus',
        comodel_name='hr.states.eval',
        inverse_name='states_eval_id',
        ondelete='cascade'
    )

    comp_average_ids = fields.One2many(
        string='Tabla de promedios y competencias',
        comodel_name='average.compe',
        inverse_name='comp_average_ids',
        ondelete='cascade'
    )


    emails_eval = fields.Char(
        string='Email de los evaluadores',
    )

    state = fields.Selection(
        [('draft', 'Borrador'),
        ('no_send_all', 'En proceso'),
        ('send', 'Enviada'),
        ('get_eval', 'Evaluaciones contestadas'),
        ('deleted', 'Evaluaciones eliminada'),
        ], 
        string='Estado',
        default='draft',
        select = True, 
        compute='get_current_state',
        store=True,
        index=True
    )

    competitions = fields.Char(
        string="Promedio en competencias",
        compute=get_average_competitions
    )

    performance = fields.Char(
        string="Promedio en desempeño",
        compute=get_average_competitions
    )

    potential = fields.Char(
        string="Promedio en potencial",
        compute=get_average_competitions
    )


    status_eval = fields.Boolean(
        string="Configuración correcta", 
        compute=check_config
    )

    exeption = fields.Char(
        string='Excepción',
        compute=get_exeption
    )

    re_send = fields.Integer(
        string='Numero de reenvio',
        default=1
    )

    is_deleted = fields.Boolean(
        string='Esta elimindado',
    )


    def get_date_end(self):
        end_eval = self.end_eval.split("-")
        _logger.warning(end_eval)
        return end_eval[2]+"-"+end_eval[1]+ "-"+end_eval[0]

    @api.multi
    def get_current_state(self):
        for evalu_id in self:
            _logger.warning("Calculando estado")
            cont_states_yesr = 0
            cont_states_send = 0
            cont_states_draft = 0
            for states_ids_id in evalu_id.states_ids:
                if states_ids_id.state == 'yes_requ':
                    cont_states_yesr = cont_states_yesr + 1
                if states_ids_id.state == 'no_requ' or states_ids_id.state == 'no_email':
                    cont_states_send = cont_states_send + 1
                if states_ids_id.state == 'no_send':
                    cont_states_draft = cont_states_draft + 1



            # if cont_states_send > 0:states_ids_id.state == 'yes_requ'states_ids_id.state == 'yes_requ'
            #   evalu_id.state = "no_send_all"
            # _logger.warning(cont_states_send)
            # _logger.warning("------------------------")
            # _logger.warning(len(evalu_id.states_ids))
            # _logger.warning("------------------------")
            # _logger.warning((cont_states_yesr + cont_states_send) == len(evalu_id.states_ids))




            if evalu_id.id_excute_plan == False:
                # evalu_id.state = "draft"

                sql = "UPDATE hr_evaluation_360 SET state = 'draft' WHERE id = "+str(evalu_id.id)+";"
                self.env.cr.execute(sql)

            if evalu_id.id_excute_plan and cont_states_yesr==False:
                evalu_id.state = "no_send_all"

                sql = "UPDATE hr_evaluation_360 SET state = 'no_send_all' WHERE id = "+str(evalu_id.id)+";"
                self.env.cr.execute(sql)

            if cont_states_send == len(evalu_id.states_ids) or ((cont_states_yesr + cont_states_send) == len(evalu_id.states_ids)):

                sql = "UPDATE hr_evaluation_360 SET state = 'send' WHERE id = "+str(evalu_id.id)+";"
                self.env.cr.execute(sql)

            if cont_states_yesr == len(evalu_id.states_ids):
                sql = "UPDATE hr_evaluation_360 SET state = 'get_eval' WHERE id = "+str(evalu_id.id)+";"
                self.env.cr.execute(sql)

            if cont_states_yesr == len(evalu_id.states_ids):
                evalu_id.state = "get_eval"

                for self_id in self:

                    if self_id.id_excute_plan:

                        answers_ids = self_id.env['admin.answers'].search([('id_excute_plan','=',self_id.id_excute_plan)])

                        evaluat = []
                        for state_id in self_id.states_ids:
                            evaluat.append(state_id.evaluators_id)

                        acom_anwers_no_in_plan = []
                        for answers_id in answers_ids:
                            #Comprueba la existencia de los evaluadores en los planes
                            if not answers_id.employee_evaluator in evaluat:
                            #   _logger.warning("Si existen en los planes")
                            # else:
                                acom_anwers_no_in_plan.append(answers_id)

                        

                        #Eliminando respuestas ya no asociadas
                        if acom_anwers_no_in_plan:
                            for ans_no_exist_eval in acom_anwers_no_in_plan:
                                _logger.warning("Eliminando respuesta")

                                # ans_no_exist_eval.sudo().unlink() 
                                # if ans_no_exist_eval:
                                #     sql = """
                                #         DELETE FROM admin_answers
                                #             WHERE id = %s
                                #     """
                                #     self_id.env.cr.execute(sql, (ans_no_exist_eval.id,))


                        comment_ids = self_id.env['commentary.360'].search([('id_excute_plan','=',self_id.id_excute_plan)])

                        evaluat = []
                        for state_id in self_id.states_ids:
                            evaluat.append(state_id.evaluators_id)

                        comment_no_in_plan = []
                        for comment_id in comment_ids:
                            #Comprueba la existencia de los evaluadores en los planes
                            if not comment_id.employee_evaluator in evaluat:
                            #   print("Si existen en los planes")
                            # else:
                                comment_no_in_plan.append(comment_id)


                        #Eliminando respuestas ya no asociadas
                        if comment_no_in_plan:
                            for comm_no_exist_eval in comment_no_in_plan:
                                _logger.warning("Eliminando respuesta")
                                _logger.warning(comm_no_exist_eval.name)

                                # if comm_no_exist_eval:
                                #     sql = """
                                #         DELETE FROM commentary_360
                                #             WHERE id = %s
                                #     """
                                #     self_id.env.cr.execute(sql, (comm_no_exist_eval.id,))

            if len(evalu_id.states_ids) == 1:
                # evalu_id.state = "no_send_all"
                sql = "UPDATE hr_evaluation_360 SET state = 'no_send_all' WHERE id = "+str(evalu_id.id)+";"
                self.env.cr.execute(sql)

            if evalu_id.is_deleted:
                # evalu_id.state = "deleted"
                sql = "UPDATE hr_evaluation_360 SET state = 'deleted' WHERE id = "+str(evalu_id.id)+";"
                self.env.cr.execute(sql)

            if cont_states_yesr and cont_states_send and cont_states_draft:
                # evalu_id.state = "no_send_all"
                sql = "UPDATE hr_evaluation_360 SET state = 'no_send_all' WHERE id = "+str(evalu_id.id)+";"
                self.env.cr.execute(sql)
        # for evalu_id in self:
        #     evaluation_no_requ = 0
        #     evaluation_send = 0
        #     evaluation_req = 0
        #     for state_id in evalu_id.states_ids:
                
        #         if state_id.state == "no_send":
        #             evaluation_no_requ = evaluation_no_requ + 1

        #         if state_id.state == "no_requ" or state_id.state == "no_emai":
        #             evaluation_send = evaluation_send + 1

        #         if state_id.state == "yes_requ":
        #             evaluation_req = evaluation_req + 1

        #     if evalu_id.id_excute_plan == False:
        #         evalu_id.state = "draft"


        #     if evalu_id.id_excute_plan and cont_states_yesr==False:
        #         evalu_id.state = "no_send_all"

        #     if cont_states_send == len(evalu_id.states_ids) or ((cont_states_yesr + cont_states_send) == len(evalu_id.states_ids)):
        #         evalu_id.state = "send"

        #     if cont_states_yesr == len(evalu_id.states_ids):
        #         evalu_id.state = "get_eval"




        # answers_ids = evalu_id.env['admin.answers'].search([('id_excute_plan','=',evalu_id.id_excute_plan)])

        # evaluat = []
        # for state_id in evalu_id.states_ids:
        #     evaluat.append(state_id.evaluators_id)

        # acom_anwers_no_in_plan = []
        # for answers_id in answers_ids:
        #     #Comprueba la existencia de los evaluadores en los planes
        #     if not answers_id.employee_evaluator in evaluat:
        #         acom_anwers_no_in_plan.append(answers_id)

        

        # #Eliminando respuestas ya no asociadas
        # # if acom_anwers_no_in_plan:
        # #     for ans_no_exist_eval in acom_anwers_no_in_plan:
        # #         _logger.warning("Eliminando respuesta")

        # #         if ans_no_exist_eval:
        # #             sql = """
        # #                 DELETE FROM admin_answers
        # #                     WHERE id = %s
        # #             """
        # #             evalu_id.env.cr.execute(sql, (ans_no_exist_eval.id,))


        # comment_ids = evalu_id.env['commentary.360'].search([('id_excute_plan','=',evalu_id.id_excute_plan)])

        # evaluat = []
        # for state_id in evalu_id.states_ids:
        #     evaluat.append(state_id.evaluators_id)

        # comment_no_in_plan = []
        # for comment_id in comment_ids:
        #     #Comprueba la existencia de los evaluadores en los planes
        #     if not comment_id.employee_evaluator in evaluat:
        #         comment_no_in_plan.append(comment_id)


        # #Eliminando respuestas ya no asociadas
        # # if comment_no_in_plan:
        # #     for comm_no_exist_eval in comment_no_in_plan:
        # #         _logger.warning("Eliminando respuesta")
        # #         _logger.warning(comm_no_exist_eval.name)

        # #         if comm_no_exist_eval:
        # #             sql = """
        # #                 DELETE FROM commentary_360
        # #                     WHERE id = %s
        # #             """
        # #             evalu_id.env.cr.execute(sql, (comm_no_exist_eval.id,))


    def get_olds_id(self):

        ids_360 = self.env['hr.evaluation.360'].search([])

        for id_360 in ids_360:
            _logger.warning(id_360.id_excute_plan)
        
            id_360.old_id_excute_plan = id_360.id_excute_plan

    def get_current_id(self):

        ids_360 = self.env['hr.evaluation.360'].search([])

        for id_360 in ids_360:
            _logger.warning(id_360.id)
        
            id_360.id_excute_plan = id_360.id



    @api.multi
    def reset_eval(self):
        self.is_deleted = False
        

    @api.multi
    def deleted_eval(self):
        self.is_deleted = True


    @api.multi
    def cancel_evaluation(self):
        comp_aver_acom = []
        for comp_aver_id in self.comp_average_ids:
            comp_aver_id.unlink()

        self.states_ids = [(0, 0, {'evaluators_id': self.name_evaluated.id, 'type_evaluators': 'collabo_eval', 'state': 'no_requ'})]
        self.state = "send"
        # raise osv.except_osv('Advertencia','%s %s %s' % ('Se reabrió una plan de evaluación es necesario modificar el evaluador agregado para que la configuración sea correcta, No puede evaluar la misma persona mas de una vez, es necesario cambiar al evaluador y presionar en el botón ‘Reenviar correo a evaluadores faltantes’.',self.name_evaluated.name, "¡Duplicado!"))



    @api.onchange('start_eval')
    def onchange_start_eval(self):
        if self.end_eval < self.start_eval and self.end_eval != False:
            self.end_eval = None
            return {'value':{},'warning':{'title':'Advertencia','message':'La fecha de fin no puede ser menor a la actual'}}

    @api.onchange('end_eval')
    def onchange_end_eval(self):
        if self.end_eval < self.start_eval and self.end_eval != False:
            self.end_eval = None
            return {'value':{},'warning':{'title':'Advertencia','message':'La fecha de fin no puede ser menor a la actual'}}

    @api.onchange('name_evaluated')
    def onchange_names_evaluators(self):
        eval_ids = []
        # eval_ids.append(self.name_evaluated.id)
        if self.name_evaluated:
            eval_ids.append((0, 0, { 'evaluators_id': self.name_evaluated.id, 'type_evaluators': 'auto_eval', 'state': 'no_send'}))
            get_job_boss = self.evaluated_id.job_id_boss.id
            get_boss = self.env['hr.employee'].search([('job_id', '=', get_job_boss)])
            if get_boss:
                if len(get_boss) == 1:
                # eval_ids.append(get_boss.id)
                    eval_ids.append((0, 0, { 'evaluators_id': get_boss.id, 'type_evaluators': 'boss_eval', 'state': 'no_send'}))

            get_collab = self.env['hr.employee'].search([('job_id.job_id_boss', '=', self.evaluated_id.id)])

            for get_coll in get_collab:
                eval_ids.append((0, 0, { 'evaluators_id': get_coll.id, 'type_evaluators': 'collabo_eval', 'state': 'no_send'}))

            eval_ids.append((0, 0, {'type_evaluators': 'partner_eval', 'state': 'no_send'}))
            eval_ids.append((0, 0, {'type_evaluators': 'client_eval', 'state': 'no_send'}))

            print(eval_ids)
            self.states_ids = eval_ids




    @api.multi
    def start(self):    
        self.id_excute_plan = self.id

        self.start_plan = self.get_data_time()
        name_evaluators_id = []
        for states_ids_id in self.states_ids:
            name_evaluators_id.append(states_ids_id.evaluators_id.name)
        
        for name_id in name_evaluators_id:
            cont_names = name_evaluators_id.count(name_id)
            if cont_names > 1:
                raise osv.except_osv('Advertencia','%s %s' % ( 'No te puede evaluar la misma persona mas de una vez, revisa el empleado evaluador llamado ',name_id))
                _logger.warning(states_ids_id.evaluators_id.name)


        
        template = self.env['mail.template'].search([('name', '=', 'Send evaluation')], limit=1)

        eval_with_email = ''
        for states_ids in self.states_ids:
            if (states_ids.state != 'yes_requ'):
                #--------------------------------
                if states_ids.evaluators_id.work_email:
                    self.emails_eval = states_ids.evaluators_id.work_email
                    _logger.warning("Se envió evaluación a")
                    _logger.warning(states_ids.state)
                    if states_ids.state == 'no_send':
                        states_ids.state = 'no_requ'

                        template.send_mail(self.id, force_send=True)
                else:
                    raise osv.except_osv('Advertencia','%s %s %s' % ( 'El usuario ',states_ids.evaluators_id.name,' no tiene usuario configurado'))
        eval_with_email = eval_with_email[:-1]



        self.state = 'no_send_all'

    
    @api.multi
    def send(self):
        self.start_plan = self.get_data_time()
        name_evaluators_id = []
        for states_ids_id in self.states_ids:
            name_evaluators_id.append(states_ids_id.evaluators_id.name)
        
        for name_id in name_evaluators_id:
            cont_names = name_evaluators_id.count(name_id)
            if cont_names > 1:
                raise osv.except_osv('Advertencia','%s %s' % ( 'No te puede evaluar la misma persona mas de una vez, revisa el empleado evaluador llamado ',name_id))
                _logger.warning(states_ids_id.evaluators_id.name)


        
        template = self.env['mail.template'].search([('name', '=', 'Send evaluation')], limit=1)

        eval_with_email = ''
        for states_ids in self.states_ids:
            if (states_ids.state != 'yes_requ'):
                #--------------------------------
                if states_ids.evaluators_id.user_id:
                    self.emails_eval = states_ids.evaluators_id.user_id.email
                    _logger.warning("Se envió evaluación a")
                    _logger.warning(states_ids.state)
                    if states_ids.state == 'no_send':
                        states_ids.state = 'no_requ'

                        template.send_mail(self.id, force_send=True)
                else:
                    raise osv.except_osv('Advertencia','%s %s %s' % ( 'El usuario ',states_ids.evaluators_id.name,' no tiene usuario configurado'))
        eval_with_email = eval_with_email[:-1]




    @api.multi
    def resend(self):
        name_evaluators_id = []
        for states_ids_id in self.states_ids:
            name_evaluators_id.append(states_ids_id.evaluators_id.name)
        
        for name_id in name_evaluators_id:
            cont_names = name_evaluators_id.count(name_id)
            if cont_names > 1:
                raise osv.except_osv('Advertencia','%s %s' % ( 'No te puede evaluar la misma persona mas de una vez, revisa el empleado evaluador llamado ',name_id))
                _logger.warning(states_ids_id.evaluators_id.name)



        
        template = self.env['mail.template'].search([('name', '=', 'Send evaluation')], limit=1)

        eval_with_email = ''
        cont_id = 0
        cont_state_req = 0
        for states_id in self.states_ids:
            if states_id.state == 'no_requ':
                cont_state_req = cont_state_req + 1
        
        _logger.warning(cont_state_req)

        for states_ids in self.states_ids:
            if (states_ids.state != 'yes_requ'):
                #--------------------------------
                cont_id = cont_id + 1
                if states_ids.evaluators_id.user_id:
                    self.emails_eval = states_ids.evaluators_id.user_id.email
                    _logger.warning("Se reenvío evaluación a   ")
                    _logger.warning(self.emails_eval)
                    _logger.warning(states_ids.state)
                    if states_ids.state == 'no_requ':
                        # states_ids.state = 'resend'
                        if states_ids.num_resend < self.re_send:
                            states_ids.num_resend = states_ids.num_resend + 1

                            template.send_mail(self.id, force_send=True)

                        else:
                            if cont_id == cont_state_req:
                                self.re_send = self.re_send + 1

                else:
                    raise osv.except_osv('Advertencia','%s %s %s' % ( 'El usuario ',states_ids.evaluators_id.name,' no tiene usuario configurado'))
        eval_with_email = eval_with_email[:-1]



    @api.multi
    def unlink(self):
        for self_id in self:
            answers_id = self.env['admin.answers'].search([('id_excute_plan', '=', int(self_id.id))], limit=1)
            if answers_id:
                _logger.warning(answers_id)
                raise osv.except_osv('Advertencia','No puedes eliminar porque ya hay respuestas de esta evaluación.')
            # else:
        return models.Model.unlink(self)


    @api.multi
    def copy(self, default=None):
        for self_id in self:
            if self_id.states_ids:
                raise osv.except_osv('Advertencia','Por razones de seguridad no puedes duplicar un plan a ejecutar.')
