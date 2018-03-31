# -*- coding: utf-8 -*-
# © <2017> <Juan Carlos VB (jcvazquez@gi.com)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models

class hr_publish_job_web(models.Model):
    _name = 'hr.publish.job.web'
    _description = 'HR PUBLISH JOB WEB'

    def get_unit(self):
        for self_id in self:
            if self_id.department_id.type_department == 'unity_cate':
                self_id.unit = self_id.department_id.name
            else:
                unit = self_id.search_unit(self_id.department_id.parent_id)
                self_id.unit = unit

    name = fields.Char(
        string="Identificador"
    )
    img_job = fields.Binary(
        string="Imagen puesto"
    )
    img_job_name = fields.Char(
        string="Imagen puesto"
    )
    equ_job = fields.Html(
        string="Requisitos"
    )
    experi_job = fields.Html(
        string="Experiencia"
    )
    fun_job = fields.Html(
        string="Funciones"
    )
    Knowle_job = fields.Html(
        string="Conocimientos"
    )
    unit = fields.Char(
        string='Unidad', 
        compute=get_unit
    )
    icon = fields.Binary(
        string='Icono bolsa de trabajo'
    )
    icon_filename = fields.Char(
        string='Nombre del archivo'
    )