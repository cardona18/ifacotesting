#!/usr/bin/env python
# -*- coding: utf-8 -*-
import base64
import logging
import sys  
from odoo.osv import osv
from odoo import SUPERUSER_ID
from odoo import http
from odoo.tools.translate import _
from odoo.http import request
from odoo.addons.web.controllers.main import serialize_exception,content_disposition


_logger = logging.getLogger(__name__)

class select_emplo(http.Controller):

    tree_str = ''
    url_img = "/web/binary/image?model=hr.employee&field=image_medium&id="


    def get_childs_by_job(self, job_org_id):

        job_org = http.request.env['hr.job'].sudo().search([('job_id_boss','=',job_org_id.id)])

        self.tree_str = self.tree_str + '<ul>'
        
        for job_org_id in job_org:

            empl_org = http.request.env['hr.employee'].sudo().search([('job_id','=',job_org_id.id)])

            if not empl_org:
                image_empl = '</br><img src="/web/static/src/img/placeholder.png"/>'
                self.tree_str = self.tree_str + '<li class="etiq">'+'NO DEFINIDO</br>'+image_empl+'</br>'+job_org_id.name
                self.get_childs_by_job(job_org_id)


            for empl_org_id in empl_org:

                if empl_org_id:
                    try:
                        image_empl = '</br><img src="%s%s"/>'
                        self.tree_str = self.tree_str + '<li class="etiq">'+empl_org_id.name+image_empl % (self.url_img,empl_org_id.id)+'</br>'+empl_org_id.job_id.name+'</br>'
                        self.get_childs_by_job(empl_org_id.job_id)
                    
                    except IndexError:
                        _logger.warning("No tiene subordinados")

                _logger.debug("EMP: %s", empl_org_id.name)
                self.get_childs_by_job(empl_org_id)

            self.tree_str = self.tree_str+'</li>'

        self.tree_str = self.tree_str + '</ul>'


    @http.route('/web/org_char/<model("hr.employee"):empl>', type='http', auth="user", website=True)
    @serialize_exception
    def generate_eval(self, empl, **kw):
        self.tree_str = ''
        _logger.info("Hola")
        job_org = http.request.env['hr.job'].sudo().search([('job_id_boss','=',empl.job_id.id)])

        if not empl.job_id.id:
            return "<h1>Tu empleado no tiene un puesto asociado</h1>"


        for job_org_id in job_org:

            _logger.warning(job_org_id.name)

            empl_org = http.request.env['hr.employee'].sudo().search([('job_id','=',job_org_id.id)])

            if not empl_org:
                image_empl = '</br><img src="/web/static/src/img/placeholder.png"/>'
                self.tree_str = self.tree_str + '<li class="etiq">'+'NO DEFINIDO</br>'+image_empl+'</br>'+job_org_id.name
                self.get_childs_by_job(job_org_id)


            for empl_org_id in empl_org:

                if not empl_org_id:
                    image_empl = '</br><img src="/web/static/src/img/placeholder.png"/>'
                    self.tree_str = self.tree_str + '<li class="etiq">'+'PUESTO VACANTE</br>'+image_empl+'</br>'+job_org_id.name
                    self.get_childs_by_job(empl_org_id.job_id)

                if empl_org_id:
                    image_empl = '</br><img src="%s%s"/>'
                    self.tree_str = self.tree_str + '<li class="etiq">'+empl_org_id.name+image_empl % (self.url_img,empl_org_id.id)+'</br>'+empl_org_id.job_id.name
                    _logger.warning("Hola mundo :#")
                    _logger.warning(empl_org_id.job_id)
                    self.get_childs_by_job(empl_org_id.job_id)
                
            self.tree_str = self.tree_str + '</li>'

            _logger.warning(self.tree_str)

        return http.request.render('hr_org_char.sele_emplo_char', {
            'url_img': self.url_img,
            'empl':empl,
            'tree_str': self.tree_str,
        })