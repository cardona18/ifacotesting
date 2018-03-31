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

class res_users_gi(models.Model):
	_inherit            = 'res.users'

	employees           = fields.Many2one('hr.employee', 'empleado')
	my_department_id        = fields.Many2one('hr.department', 'Departemento')

	def get_employee_depatment(self):
		self.ensure_one()

		employee = self.env['hr.employee'].search([('user_id','=',self.id)], limit=1)

		employees = employee
		my_department = employee.department_id.id

		if(my_department):

			return my_department

		return False