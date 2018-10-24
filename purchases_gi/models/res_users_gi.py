# -*- coding: utf-8 -*-
# © <2016> <Juan Carlos Vazquez Beas (jcvazquez@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# 1 : imports of python lib
import locale
import logging
import sys
# 2 :  imports of openerp
from openerp import models, fields, api
from openerp import SUPERUSER_ID
from openerp import tools
from openerp import models, fields,api
from openerp.osv import osv
from openerp.exceptions import ValidationError
#from openerp.osv import fields, osv

_logger = logging.getLogger(__name__)

class res_users_gi(models.Model):
    """
    Hereda el modelo de para agregar una función necesaria en el módulo de compras.
    """
    _inherit            = 'res.users'

    def get_employee_depatment(self):
        """
        Regresa el departamento esto con la finalidad de restringir la visualización de registros por departamentos.
        """
        self.ensure_one()

        employee = self.env['hr.employee'].search([('user_id','=',self.id)], limit=1)
        if(employee.department_id):
            return employee.department_id.id
        else:
            raise ValidationError('Se debe de configurar el departamento en el empleado.')
        return False