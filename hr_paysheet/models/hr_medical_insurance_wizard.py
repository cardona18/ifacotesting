# -*- coding: utf-8 -*-
# © <2017> <Omar Torres Silva (otorres@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime
import os

from openerp import fields, models, api
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT

class hr_medical_insurance_wizard(models.TransientModel):
    _name = 'hr.medical.insurance.wizard'
    _description = 'HR MEDICAL INSURANCE WIZARD'

    limit_date = fields.Date(
        string='Fecha de corte'
    )

    @api.multi
    def compute_medical_insurance(self):

        os.environ['TZ'] = "America/Mexico_City"

        for employee in self.env['hr.employee'].sudo().search([]):

            if employee.has_medical_insurance:

                from_date = datetime.strptime(employee.birth_date, DEFAULT_SERVER_DATE_FORMAT)
                to_date = datetime.strptime(self.limit_date, DEFAULT_SERVER_DATE_FORMAT)

                years = int((to_date - from_date).days / 365)

                row = self.env['hr.medical.insurance'].search([('to_years','>=', years), ('from_years','<=', years)], limit=1)

                if row.id:
                    employee.medical_insurance = row.male if employee.emp_gender == 'H' else row.female
                else:
                    employee.medical_insurance = 0

            else:
                employee.medical_insurance = 0
