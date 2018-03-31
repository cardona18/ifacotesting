# -*- coding: utf-8 -*-
# © <2017> <Omar Torres Silva (otorres@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api

class hr_employee_wage_wizard(models.TransientModel):
    _name = 'hr.employee.wage.wizard'
    _description = 'HR EMPLOYEE WAGE WIZARD'

    rtype = fields.Selection(
        string='Exportar',
        size=1,
        default='P',
        selection=[
            ('P', 'Vista previa'),
            ('X', 'Hoja de cálculo')
        ]
    )
    company_ids = fields.Many2many(
        string='Empresas',
        comodel_name='res.company'
    )

    @api.multi
    def build_report_action(self):

        cids = ','.join(str(company.id) for company in self.company_ids)

        return {
            'type' : 'ir.actions.act_url',
            'url': '/web/reports/hr_wage_report?ids=%s&export_type=%s' % (cids, self.rtype),
            'target': 'self' if self.rtype == 'X' else 'new',
        }