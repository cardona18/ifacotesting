#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from odoo import http, _
from odoo.addons.website.models.website import slug
from odoo.http import request
import sys  

_logger = logging.getLogger(__name__)

class Evaluations(http.Controller):

    @http.route('/web/evaluations/', type='http', auth="user", website=True)
    def generate_eval(self, **kw):

        my_evaluations = []

        evaluations = http.request.env['hr.evaluation.360'].sudo().search([('state','=','send')])

        current_employee = http.request.env.user.employee_ids
        print(current_employee)

        no_id = http.request.env['hr.states.eval'].sudo().search([('states_eval_id', '=', None)])
        no_id.unlink()

        for evaluations_ids in evaluations:
            evaluation = http.request.env['hr.states.eval'].sudo().search([('evaluators_id','=',current_employee.id), ('state','=','no_requ')])

            for evaluation_id in evaluation:
                my_evaluations.append(evaluation_id.states_eval_id) 

        my_evaluations = list(set(my_evaluations))
        print(my_evaluations)

        genaral_questions = http.request.env['hr.general.quest.360'].sudo().search([])

        no_evaluation = False
        if len(my_evaluations) == False:
            no_evaluation = True

        return http.request.render('hr_evaluation_360.evaluations_template', {
            'no_evaluation':no_evaluation,
            'my_evaluations': my_evaluations,
            'current_employee': current_employee,
            'genaral_questions': genaral_questions,
        })


    @http.route('/web/request_data/', type='http', auth="user")
    def request_data_answ(self, **kw):

        for data_form in kw:

            att_answ = data_form.split('-')


            if att_answ[0] == 'comment':
                answers = http.request.env['commentary.360']
                yes_comment = http.request.env['commentary.360'].sudo().search([('evalu_plan','=', int(att_answ[2])), ('employee_evaluator','=', int(att_answ[3]))])
                if yes_comment:
                    _logger.warning("Ya existe el comentario")
                else:
                    answers.sudo().create({'name':kw[data_form],'evalu_plan': att_answ[2], 'employee_evaluator': att_answ[3]})
            else:

                exc_eval = http.request.env['hr.states.eval'].sudo().search([('evaluators_id', '=', int(att_answ[4])), ('states_eval_id', '=', int(att_answ[3]))])


                answers = http.request.env['admin.answers']
                if att_answ[2] == 'None':
                    #comprobar si ya se capturó la respuesta

                    request_answers = http.request.env['admin.answers'].sudo().search([('quest_gen','=', int(att_answ[0])), ('id_excute_plan','=', int(att_answ[3])),('employee_evaluator','=',int(att_answ[4]))])
                    if request_answers:
                        _logger.warning("No se creó la respuesta")
                    else:
                        answers.sudo().create({'name':kw[data_form],'quest_gen': att_answ[0], 'is_general': True, 'evalu_plan': att_answ[3], 'employee_evaluator': att_answ[4], 'type_evaluators': exc_eval.type_evaluators, 'general_type': att_answ[5]})
                else:
                    #comprobar si ya se capturó la respuesta
                    request_answers = http.request.env['admin.answers'].sudo().search([('quest','=', int(att_answ[0])), ('id_excute_plan','=', int(att_answ[3])),('employee_evaluator','=',int(att_answ[4]))])
                    #_logger.warning(request_answers)
                    if request_answers:
                        _logger.warning("No se creó la respuesta")
                    else:

                        answers.sudo().create({'name':kw[data_form],'quest': att_answ[0], 'comp': att_answ[2], 'evalu_plan': att_answ[3], 'employee_evaluator': att_answ[4], 'type_evaluators': exc_eval.type_evaluators})

        #Update states of evaluation 360°
        exc_eval.state = 'yes_requ'

        state_eval = http.request.env['hr.states.eval'].sudo().search([('states_eval_id', '=', int(att_answ[3]))])
        current_eval = http.request.env['hr.evaluation.360'].sudo().search([('id', '=', int(att_answ[3]))],limit= 1)

        if current_eval:

            count_states_yes_req = 0
            for state_eval_ids in state_eval:
                if state_eval_ids.state == 'yes_requ':
                    # print("Hola")
                    count_states_yes_req = count_states_yes_req + 1
            if len(state_eval) == count_states_yes_req:
                current_eval.sudo().state = 'get_eval'

            return http.request.render('hr_evaluation_360.evaluations_end', {})

        else:
             return """<html><head><script>
                        alert("Evaluación contestada con éxito");
                        window.location = '%s/' + encodeURIComponent("%s" + location.hash);
                    </script></head></html>
                    """ % ('/web/evaluations', '')


    @http.route('/web/my_evaluations/', type='http', auth="user", website=True)
    def my_evaluations(self, **kw):
        # LOAD UTF-8 AS DEFAULT
        reload(sys)
        sys.setdefaultencoding('utf-8')

        evalu = []

        current_employee = http.request.env.user.employee_ids

        evaluations = http.request.env['hr.evaluation.360'].sudo().search([('state','=','get_eval'), ('name_evaluated','=',current_employee.id)])
        for eva in evaluations:
            if eva.state == 'get_eval':
                evalu.append(eva)

        if evalu:
            return http.request.render('hr_evaluation_360.my_reports', {
            'my_evaluations': evalu,
            })

        else:
            return http.request.render('hr_evaluation_360.my_reports_no_eval', {})



    @http.route('/web/select_report/', type='http', auth="user")
    def select_report(self, **kw):
        # LOAD UTF-8 AS DEFAULT
        _logger.warning("Iniciando panel de control")
        reload(sys)
        sys.setdefaultencoding('utf-8')

        evalu_draft_n = 0
        evalu_send_n = 0
        evalu = []

        draft_evaluations = http.request.env['hr.evaluation.360'].sudo().search([])
        for eva in draft_evaluations:
            _logger.warning(eva.state)

            if eva.state == 'draft':
                evalu_draft_n = evalu_draft_n + 1
                # evalu_draft.append(eva)

            if eva.state == 'no_send_all' or eva.state == 'send':
                evalu_send_n = evalu_send_n + 1

            if eva.state == 'get_eval':
                evalu.append(eva)

        _logger.warning("Verificando estados")

        if evalu:

            avarage_evaluation_ans = float((evalu_send_n)*100)/float(len(evalu)+(evalu_send_n))

            avarage_done = 100-avarage_evaluation_ans

            _logger.warning(evalu_draft_n)
            _logger.warning(evalu_send_n)
            _logger.warning(format((avarage_evaluation_ans),'.2f'))
            _logger.warning(format((avarage_done),'.2f'))


            return http.request.render('hr_evaluation_360.select_report_template', {
                'my_evaluations': evalu,
                'evalu_done':len(evalu),
                'evalu_draft':evalu_draft_n,
                'evalu_send':evalu_send_n,
                'average_to_be_done':format((avarage_evaluation_ans),'.2f'),
                'avarage_done':format((avarage_done),'.2f'),
                })
        else:
            return """<html><head><script>
                        alert("No hay ninguna evaluación que consultar");
                        window.close();
                    </script></head></html>
                    """ 



    @http.route('/web/reports/', type='http', auth="user", csrf=False)
    def general_report(self, **kw):
        # LOAD UTF-8 AS DEFAULT

        reload(sys)
        sys.setdefaultencoding('utf-8')

        action_win = False
        try:
            if kw['action_win']:
                action_win = True
        except KeyError:
                action_win = False
        
        evaluations = http.request.env['hr.evaluation.360'].sudo().search([('state','=','get_eval'),('id','=',kw["evaluation_com"])])

        if not evaluations:
            return """<html><head><script>
                        alert("No hay ninguna evaluación que consultar");
                        window.close();
                    </script></head></html>
                    """ 

        eval_data = []
        comp_data = []
        comp_ids  = []
        best_data = []
        points_aco = 0
        points = 0
        calf = 0

        for eval_id in evaluations:
            for ids_eval in eval_id.name.config_ids:

                answers = http.request.env['admin.answers'].sudo().search([('id_excute_plan','=',eval_id.id),('comp','=',ids_eval.comp_id.id),('is_general','=',False)])
                points = 0
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
                
                if len(answers):
                    calf = points / len(answers) /10  


                avera_result = calf*ids_eval.point_comp/10
                comp_id_enc = (ids_eval.comp_id.name.encode("latin1"))
                comp_ids.append(ids_eval.comp_id)
                eval_data.append(comp_id_enc)
                comp_data.append(avera_result)
                best_data.append(ids_eval.point_comp)

                points_aco = points_aco+points


        '''

 _____            __ _                 _        _                              
|  __ \          / _(_)               | |      | |                             
| |  \/_ __ __ _| |_ _  ___ __ _    __| | ___  | |__   __ _ _ __ _ __ __ _ ___ 
| | __| '__/ _` |  _| |/ __/ _` |  / _` |/ _ \ | '_ \ / _` | '__| '__/ _` / __|
| |_\ \ | | (_| | | | | (_| (_| | | (_| |  __/ | |_) | (_| | |  | | | (_| \__ \
 \____/_|  \__,_|_| |_|\___\__,_|  \__,_|\___| |_.__/ \__,_|_|  |_|  \__,_|___/
                                                                               
                                                                               
        '''
        auto_eval = 0
        boss_eval = 0
        collabo_eval = 0
        partner_eval = 0
        client_eval = 0

        auto_eval_cont = 0
        boss_eval_cont = 0
        collabo_eval_cont = 0
        partner_eval_cont = 0
        client_eval_cont = 0
        my_auto_eval_reslt = 0
        general_eval_reslt = 0

        bar_names = []
        bar_result = []
        name_evalutors = [] 
        questions_acom = [] 
        my_auto_eval   = []
        general_eval_res = []
        general_average_aco = []    #Acomoulador para obtener el promedio general
        general_average_cont = []   #contador para obtener el promedio general
        general_average = 0

        for ev_states_ids in evaluations.states_ids:
            if ev_states_ids.type_evaluators == 'auto_eval':
                points = 0
                auto_eval_cont = auto_eval_cont+1

                answers = http.request.env['admin.answers'].sudo().search([('id_excute_plan','=',eval_id.id),('employee_evaluator','=',ev_states_ids.evaluators_id.id),('is_general','=',False)])
                questions_acom.append(answers)
                name_evalutors.append(ev_states_ids.evaluators_id.name)
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



                calf = points / len(answers) /10

                auto_eval = auto_eval + calf


            if ev_states_ids.type_evaluators == 'boss_eval':
                boss_eval_cont = boss_eval_cont+1
                points = 0
                answers = http.request.env['admin.answers'].sudo().search([('id_excute_plan','=',eval_id.id),('employee_evaluator','=',ev_states_ids.evaluators_id.id),('is_general','=',False)])
                questions_acom.append(answers)
                name_evalutors.append(ev_states_ids.evaluators_id.name)
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
                        my_auto_eval_reslt
                        points = points + 100
                    if answers_id.name == 'no':
                        points = points + 0
                    if answers_id.name.isdigit():
                        points = points + float(answers_id.name)

                calf = points / len(answers) /10
                boss_eval = boss_eval + calf
            

            if ev_states_ids.type_evaluators == 'collabo_eval':
                points = 0
                collabo_eval_cont = collabo_eval_cont +1
                answers = http.request.env['admin.answers'].sudo().search([('id_excute_plan','=',eval_id.id),('employee_evaluator','=',ev_states_ids.evaluators_id.id),('is_general','=',False)])
                questions_acom.append(answers)
                name_evalutors.append(ev_states_ids.evaluators_id.name)
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

                calf = points / len(answers) /10
                collabo_eval = collabo_eval + calf
            

            if ev_states_ids.type_evaluators == 'partner_eval':
                points = 0
                partner_eval_cont = partner_eval_cont +1
                answers = http.request.env['admin.answers'].sudo().search([('id_excute_plan','=',eval_id.id),('employee_evaluator','=',ev_states_ids.evaluators_id.id),('is_general','=',False)])
                questions_acom.append(answers)
                name_evalutors.append(ev_states_ids.evaluators_id.name)
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

                calf = points / len(answers) /10
                partner_eval = partner_eval + calf
            

            if ev_states_ids.type_evaluators == 'client_eval':
                points = 0
                client_eval_cont = client_eval_cont+1
                answers = http.request.env['admin.answers'].sudo().search([('id_excute_plan','=',eval_id.id),('employee_evaluator','=',ev_states_ids.evaluators_id.id),('is_general','=',False)])
                questions_acom.append(answers)
                name_evalutors.append(ev_states_ids.evaluators_id.name)
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

                calf = points / len(answers) /10
                client_eval = client_eval + calf

        if auto_eval_cont:
            auto_ev = "Autoevaluación"
            auto_ev = auto_ev.encode("latin1")
            bar_names.append(auto_ev)
            bar_result.append(auto_eval/auto_eval_cont)
            my_auto_eval.append(auto_eval/auto_eval_cont)
            general_average_aco.append(auto_eval)
        if boss_eval_cont:
            bar_names.append("Jefe"+"("+str(boss_eval_cont)+")")
            bar_result.append(boss_eval/boss_eval_cont)
            general_eval_res.append(boss_eval/boss_eval_cont)
            general_average_aco.append(boss_eval)
        if collabo_eval_cont:
            bar_names.append("Subordinados"+"("+str(collabo_eval_cont)+")")
            bar_result.append(collabo_eval/collabo_eval_cont)
            general_eval_res.append(collabo_eval/collabo_eval_cont)
            general_average_aco.append(collabo_eval)
        if partner_eval_cont:
            parn_cond = "Compañeros"+"("+str(partner_eval_cont)+")"
            parn_cond = parn_cond.encode("latin1")
            bar_names.append(parn_cond)
            bar_result.append(partner_eval/partner_eval_cont)
            general_eval_res.append(partner_eval/partner_eval_cont)
            general_average_aco.append(partner_eval)
        if client_eval_cont:
            bar_names.append("Cliente"+"("+str(client_eval_cont)+")")
            bar_result.append(client_eval/client_eval_cont)
            general_eval_res.append(client_eval/client_eval_cont)
            general_average_aco.append(client_eval)


        for general_average_aco_id in general_average_aco:
            general_average = general_average + general_average_aco_id

        general_average = format(general_average / len(evaluations.states_ids),'.2f')

        for my_auto_eval_res_id in my_auto_eval:
            my_auto_eval_reslt = my_auto_eval_reslt + my_auto_eval_res_id

        for general_eval_res_id in general_eval_res:
            general_eval_reslt = general_eval_reslt + general_eval_res_id

        general_eval_reslt = general_eval_reslt/len(general_eval_res)


        comp_data = [ '%.2f' % elem for elem in comp_data ]

        evaluations = http.request.env['hr.evaluation.360'].sudo().search([('state','=','get_eval'),('id','=',kw["evaluation_com"])])
        
        points_per = 0.0
        cont_points_per = 0
        points_pot = 0.0
        cont_points_pot = 0
        aco_performance = []
        aco_potential = []

        for states_ids_id in evaluations.states_ids:

            answers_gen = http.request.env['admin.answers'].sudo().search([('id_excute_plan','=',kw['evaluation_com']),('is_general','=',1),('employee_evaluator','=',states_ids_id.evaluators_id.id)])
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
                    
                    cont_points_pot = cont_points_pot + 1

                    aco_potential.append(answers_gen_id)



        if cont_points_per:
            points_per = (points_per/cont_points_per/10)
        else:
            points_per = (points_per/10)

        if cont_points_pot: 

            points_pot = points_pot/cont_points_pot/10

        else:
            points_pot = (points_pot/10) 


        bar_result = [ '%.2f' % elem for elem in bar_result ]
        my_auto_eval_reslt = format(my_auto_eval_reslt,'.2f')
        general_eval_reslt = format(general_eval_reslt,'.2f')


        cont_eval_data = 0
        format_eval_data = []
        for eval_data_id in eval_data:
            format_eval_data.append(eval_data_id+' ('+str(comp_data[cont_eval_data])+' puntos de '+str(best_data[cont_eval_data])+')')
            cont_eval_data = cont_eval_data + 1


        comment_eval = http.request.env['commentary.360'].sudo().search([('evalu_plan','=',evaluations.id)])



        '''
 _____            __ _                                                           _   _                
|  __ \          / _(_)                                                         | | (_)               
| |  \/_ __ __ _| |_ _  ___ __ _ ___    ___ ___  _ __ ___  _ __   __ _ _ __ __ _| |_ ___   ____ _ ___ 
| | __| '__/ _` |  _| |/ __/ _` / __|  / __/ _ \| '_ ` _ \| '_ \ / _` | '__/ _` | __| \ \ / / _` / __|
| |_\ \ | | (_| | | | | (_| (_| \__ \ | (_| (_) | | | | | | |_) | (_| | | | (_| | |_| |\ V / (_| \__ \
 \____/_|  \__,_|_| |_|\___\__,_|___/  \___\___/|_| |_| |_| .__/ \__,_|_|  \__,_|\__|_| \_/ \__,_|___/
                                                          | |                                         
                                                          |_|                                         
        '''



        cont_comp = 0
        average_comp = []
        for best_data_id in best_data:
            average_comp.append(format((10*(float(comp_data[cont_comp])))/float(best_data_id),'.2f'))
            cont_comp = cont_comp + 1




        cont_add_comp = 0
        acom_averege_comp = []
        if evaluations.comp_average_ids:
            _logger.warning("Datos ya capturados")
        else:
            for average_comp_id in average_comp:
                acom_averege_comp.append((0, 0, { 'comp_id': comp_ids[cont_add_comp], 'average_comp': average_comp_id}))
                cont_add_comp = cont_add_comp + 1



            evaluations.sudo().comp_average_ids = acom_averege_comp


        '''

______                _ _            _                                  _                                _       
| ___ \              | | |          | |                                (_)                              (_)      
| |_/ /___  ___ _   _| | |_ __ _  __| | ___  ___   _ __   ___  _ __     _  ___ _ __ __ _ _ __ __ _ _   _ _  __ _ 
|    // _ \/ __| | | | | __/ _` |/ _` |/ _ \/ __| | '_ \ / _ \| '__|   | |/ _ \ '__/ _` | '__/ _` | | | | |/ _` |
| |\ \  __/\__ \ |_| | | || (_| | (_| | (_) \__ \ | |_) | (_) | |      | |  __/ | | (_| | | | (_| | |_| | | (_| |
\_| \_\___||___/\__,_|_|\__\__,_|\__,_|\___/|___/ | .__/ \___/|_|      | |\___|_|  \__,_|_|  \__, |\__,_|_|\__,_|
                                                  | |                 _/ |                      | |              
                                                  |_|                |__/                       |_|       
        '''

        name_type_job = ' '
        job_type = evaluations.name_evaluated.job_id.category_job

        eval_job = []
        evaluations_same = http.request.env['hr.evaluation.360'].sudo().search([])
        for eva_same_id in evaluations_same:
            if eva_same_id.state == 'get_eval':
                if eva_same_id.name_evaluated.job_id.category_job == job_type:
                    eval_job.append(eva_same_id)


        if evaluations.name_evaluated.job_id.category_job == 'is_director':
            name_type_job = 'Promedio de Directores'
        if evaluations.name_evaluated.job_id.category_job == 'is_manager':
            name_type_job = 'Promedio de Gerentes'
        if evaluations.name_evaluated.job_id.category_job == 'is_boss':
            name_type_job = 'Promedio de Jefes'
        if evaluations.name_evaluated.job_id.category_job == 'contributor_ind':
            name_type_job = 'Promedio de Contribuidor individual'
        if evaluations.name_evaluated.job_id.category_job == 'operator':
            name_type_job = 'Promedio de Operador'



            



        acom_comp_same = []
        acom_average_comp_same = []
        no_complete_aver_capt_same = None
        for eval_id in eval_job:
            if eval_id.comp_average_ids:
                _logger.warning("Todos los datos estan completos(Promedios competencias)")
            else:
                no_complete_aver_capt_same = eval_id

            for com_average_id in eval_id.comp_average_ids:
                for compet_ids in comp_ids:
                    if com_average_id.comp_id.id == compet_ids.id:
                        acom_comp_same.append(compet_ids)
                        acom_average_comp_same.append(com_average_id.average_comp)



        #Busca y promediar competencias
        cont_repit_com_same = []
        sum_average_com_same = []

        cont_comp_pos = 0
        for comp_id in comp_ids:
            cont_comp_rep = 0
            cont_comp_sum = 0
            for acom_comp_id in acom_comp_same:
                if acom_comp_id.id == comp_id.id:
                    try:
                        if sum_average_com_same[cont_comp_pos]:
                            sum_average_com_same[cont_comp_pos] = sum_average_com_same[cont_comp_pos] + acom_average_comp_same[cont_comp_sum]
                        else:
                            sum_average_com_same[cont_comp_pos] = acom_average_comp_same[cont_comp_sum]
                    except (IndexError, ValueError):
                        sum_average_com_same.append(acom_average_comp_same[cont_comp_sum])

                    cont_comp_rep = cont_comp_rep + 1
                
                cont_comp_sum = cont_comp_sum + 1

            cont_repit_com_same.append(cont_comp_rep)
            cont_comp_pos = cont_comp_pos + 1


        average_by_comp_same = []
        cont_rep_same = 0

        for repit_comp_id in cont_repit_com_same:

            if repit_comp_id == 0:
                average_by_comp_same.append(format((sum_average_com_same[cont_rep_same]),'.2f'))
                cont_rep_same = cont_rep_same + 1 
            else:

                average_by_comp_same.append(format((sum_average_com_same[cont_rep_same] / repit_comp_id),'.2f'))
                cont_rep_same = cont_rep_same + 1 


        '''

______                _ _            _                                             _           
| ___ \              | | |          | |                                           | |          
| |_/ /___  ___ _   _| | |_ __ _  __| | ___  ___    __ _  ___ _ __   ___ _ __ __ _| | ___  ___ 
|    // _ \/ __| | | | | __/ _` |/ _` |/ _ \/ __|  / _` |/ _ \ '_ \ / _ \ '__/ _` | |/ _ \/ __|
| |\ \  __/\__ \ |_| | | || (_| | (_| | (_) \__ \ | (_| |  __/ | | |  __/ | | (_| | |  __/\__ \
\_| \_\___||___/\__,_|_|\__\__,_|\__,_|\___/|___/  \__, |\___|_| |_|\___|_|  \__,_|_|\___||___/
                                                    __/ |                                      
                                                   |___/                  
        '''


        eval_finish = []
        evaluations_finish = http.request.env['hr.evaluation.360'].sudo().search([])
        for eva_finish_id in evaluations_finish:
            if eva_finish_id.state == 'get_eval':
                eval_finish.append(eva_finish_id)


        acom_comp = []
        acom_average_comp = []
        no_complete_aver_capt = None
        # #_logger.warning(eva_finish_id)
        for eval_id in eval_finish:
            if eval_id.comp_average_ids:
                _logger.warning("Todos los datos estan completos(Promedios competencias)")
            else:
                no_complete_aver_capt = eval_id

            for com_average_id in eval_id.comp_average_ids:
                for compet_ids in comp_ids:
                    if com_average_id.comp_id.id == compet_ids.id:
                        acom_comp.append(compet_ids)
                        acom_average_comp.append(com_average_id.average_comp)


        #Busca y promediar competencias
        cont_repit_com = []
        sum_average_com = []
        cont_comp_pos = 0
        for comp_id in comp_ids:
            cont_comp_rep = 0
            cont_comp_sum = 0
            for acom_comp_id in acom_comp:
                if acom_comp_id.id == comp_id.id:
                    try:
                        if sum_average_com[cont_comp_pos]:
                            sum_average_com[cont_comp_pos] = sum_average_com[cont_comp_pos] + acom_average_comp[cont_comp_sum]
                        else:
                            sum_average_com[cont_comp_pos] = acom_average_comp[cont_comp_sum]
                    except (IndexError, ValueError):
                        sum_average_com.append(acom_average_comp[cont_comp_sum])

                    cont_comp_rep = cont_comp_rep + 1
                
                cont_comp_sum = cont_comp_sum + 1

            cont_repit_com.append(cont_comp_rep)
            cont_comp_pos = cont_comp_pos + 1


        average_by_comp = []
        cont_rep = 0
        for repit_comp_id in cont_repit_com:

            if repit_comp_id == 0:
                average_by_comp.append(format((sum_average_com[cont_rep]),'.2f'))
                cont_rep = cont_rep + 1 
            else:
                average_by_comp.append(format((sum_average_com[cont_rep] / repit_comp_id),'.2f'))
                cont_rep = cont_rep + 1 

        users_with_per = http.request.env['res.groups'].sudo().search([('name','=','Jefe Desarrollo Organizacional')])


        if http.request.env.user not in users_with_per.users and evaluations.name_evaluated.user_id != http.request.env.user:
            return """<html><head><script>
                        window.location = '/web/my_evaluations/';
                    </script></head></html>
                    """
            

        return http.request.render('hr_evaluation_360.report_template', {
            'my_evaluations': evaluations,
            'eval_data': format_eval_data,
            'comp_data': comp_data,
            'best_data': best_data,
            'bar_names': bar_names,
            'bar_result': bar_result,
            'general_average': general_average,
            'name_evalutors': name_evalutors,
            'questions_acom': questions_acom,
            'report_sel':kw['report_sel'],
            'my_auto_eval_reslt':my_auto_eval_reslt,
            'general_eval_reslt':general_eval_reslt,
            'points_per':points_per,
            'points_pot':points_pot,
            'answers_gen':answers_gen,
            'aco_performance':aco_performance,
            'aco_potential':aco_potential,
            'comment_eval':comment_eval,
            'comp_names':eval_data,
            'average_comp':average_comp,
            'average_by_comp':average_by_comp,
            'job_average':average_by_comp_same,
            'eval_no_comple': no_complete_aver_capt,
            'name_type_job':name_type_job,
            'action_win':action_win,
            'cont_repit_com_same':cont_repit_com_same,
            'cont_repit_com':cont_repit_com,
            'comp_ids':comp_ids,
            })

    @http.route('/web/yes_360/', type='http', auth='public', website=True)
    def yes_required_360(self, **kw):
        return http.request.render('hr_evaluation_360.yes_request_360', {})
