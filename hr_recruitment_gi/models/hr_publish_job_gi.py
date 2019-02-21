# -*- coding: utf-8 -*-
# © <2016> <Juan Carlos Vazquez Beas (jcvazquez@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# 1 : imports of python lib
import locale
import logging
import sys
# import smtplib
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime
from dateutil import tz
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

class hr_publish_job_gi(models.Model):
	_name = 'hr.publish.job.gi'
	_description = 'Modulo para publicar vacantes'

	name        =   fields.Char(string="Nombre del puesto", size=200, required="1")
	# publica     =   fields.Selection([('intra', 'Publicar en la intranet'),
	# 							('web', 'Publicar en el sitio externo'),
	# 							('intra_web', 'Publicar en ambos')], string='Lugar de publicación', required="1")

	Requ_job    =   fields.Html(string="Requisitos")
	experi_job	=	fields.Html(string="Experiencia")
	fun_job  	=   fields.Html(string="Funciones")
	Knowle_job  =   fields.Html(string="Conocimientos")
	state               = fields.Selection([('draft', 'Borrador'),
										('published', 'Publicado'),
										('not_published', 'No publicado')
										], string='Estado', default='draft')
	@api.multi
	def published(self):
		"""Change the request status to published and notify to applicant user

		@return send_mail function result"""

		self.state = 'published'

	@api.multi
	def not_published(self):
		"""Change the request status to not_published and notify to applicant user

		@return send_mail function result"""

		self.state = 'not_published'
