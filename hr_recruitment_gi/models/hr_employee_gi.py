# -*- coding: utf-8 -*-
# © <2016> <Juan Carlos Vazquez Beas (jcvazquez@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# 1 : imports of python lib
import locale
import logging
import sys  
from openerp import models, fields, api
from openerp import SUPERUSER_ID
from openerp import tools
from openerp.osv import osv
from openerp.tools.translate import _


reload(sys)  
sys.setdefaultencoding('utf8')
_logger = logging.getLogger(__name__)

## Documentation for a class.
#  Modificaciones al catálogo de empleados para el funcionamiento del módulo de reclutamiento y selección de personal.
#  Sobrescribiendo el modelo hr.employee
class hr_employee_gi(models.Model):
    _inherit            = 'hr.employee'
    
    job_id              = fields.Many2one('hr.job', 'Puesto vacante', ondelete='cascade')
    department_id       = fields.Many2one(related='job_id.department_id', string="Árbol de jerarquía", readonly=True, store=True)
    empl_temp           = fields.Boolean('Empleado temporal')



    ## Documentation for a function.
    #  Esta función comprueba la cantidad de puestos autorizados 
    @api.onchange('job_id')
    def onchange_job_id_num_aut_emplo(self):
        num_empl_allowed    = self.job_id.x_num_aut_emplo
        num_empl_current    = self.job_id.no_of_employee_cur
        x_tem_emplo         = self.job_id.x_tem_emplo

        if self.active:
            if self.job_id.id != False:
                if num_empl_current == num_empl_allowed:

                    if not self.empl_temp:
                        if x_tem_emplo > 0:
                            self.job_id  = None
                            return {'value':{},'warning':{'title':'Advertencia','message':'Solo hay plazas temporales para este puesto, si se desea agregar un puesto temporal activa la casilla "Empleado temporal" y vuelve a intentarlo, si el empleado no es temporal comunícate con el gerente de recursos humanos.'}}
                        else:
                            self.job_id  = None
                            return {'value':{},'warning':{'title':'Advertencia','message':'No puedes seleccionar este puesto por que todas las vacantes ya estan ocupadas'}}


                if self.empl_temp:
                    _logger.warning(num_empl_allowed + x_tem_emplo)
                    if num_empl_current >= num_empl_allowed + x_tem_emplo:
                        self.job_id  = None
                        return {'value':{},'warning':{'title':'Advertencia','message':'No puedes seleccionar este puesto por que todas las vacantes ya estan ocupadas'}}


