# -*- coding: utf-8 -*-
# © <2016> <Omar Torres Silva (otorres@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api

class hr_employee_leave(models.TransientModel):
    _name = 'hr.employee.leave'
    _description = 'HR EMPLOYEE LEAVE'

    def default_employee_id(self):
        return self.env.context.get('active_id',False)

    employee_id = fields.Many2one(
        string='Empleado',
        comodel_name='hr.employee',
        default=default_employee_id
    )
    leave_type = fields.Selection(
        string='Tipo de baja',
        size=10,
        selection=[
            ('LEAVE', 'Baja'),
            ('CHANGE', 'Cambio de empresa')
        ]
    )
    current_company_id = fields.Many2one(
        string='Empresa actual',
        comodel_name='res.company'
    )
    new_company_id = fields.Many2one(
        string='Cambiar a',
        comodel_name='res.company'
    )
    leave_date = fields.Date(
        string='Fecha de baja'
    )
    leave_ss_date = fields.Date(
        string='Fecha de baja IMSS'
    )
    reg_date = fields.Date(
        string='Fecha de alta'
    )

    @api.multi
    def employee_leave_action(self):

        if self.leave_type == 'LEAVE':

            for contract in self.env['hr.contract'].search([('employee_id', '=', self.employee_id.id)]):
                contract.date_end = self.leave_date
                contract.active = False

            self.employee_id.ss_out_date = self.leave_ss_date
            self.employee_id.out_date = self.leave_date
            self.employee_id.active = False

        if self.leave_type == 'CHANGE':

            contract = self.env['hr.contract'].search([('employee_id', '=', self.employee_id.id), ('for_paysheet', '=', True)], limit=1)

            new_contract = contract.copy()
            new_employee = self.employee_id.copy()

            # UPDATE EMPLOYEES
            self.employee_id.out_date = self.leave_date
            self.employee_id.ss_out_date = self.leave_ss_date
            self.employee_id.history_id = self.employee_id.old_id
            self.employee_id.old_id = False
            self.employee_id.active = False

            new_employee.company_id = self.new_company_id.id
            new_employee.read_company_name = self.new_company_id.name
            new_employee.employer_registration = False
            new_employee.ss_in_date = self.reg_date
            new_employee.reg_date = self.reg_date
            new_employee.out_date = False
            new_employee.ss_out_date = False
            new_employee.history_id = 0
            new_employee.sudo().write({
                'old_id': new_employee.generate_key(self.new_company_id.id)
            })

            # UPDATE CONTRACTS
            contract.date_end = self.leave_date
            contract.active = False

            new_contract.state = 'approved'
            new_contract.company_id = self.new_company_id.id
            new_contract.employee_id = new_employee.id
            new_contract.date_end = False
            new_contract.date_start = self.reg_date

            for benefit in contract.benefit_ids:
                self.env['hr.paysheet.benefit'].create({
                    'concept_id': benefit.concept_id.id,
                    'btype': benefit.btype,
                    'amount': benefit.amount,
                    'table_id': benefit.table_id.id,
                    'contract_id': new_contract.id
                })

            self.env['hr.company.change'].create({
                'employee_id': self.employee_id.id,
                'last_company_id': self.employee_id.company_id.id,
                'new_company_id': self.new_company_id.id
            })

            return {
                'name': 'Empleados',
                'view_mode': 'form',
                'view_id': False,
                'views': [(False,'form')],
                'view_type': 'form',
                'res_id' : new_employee.id,
                'active_id' : new_employee.id,
                'res_model': 'hr.employee',
                'type': 'ir.actions.act_window'
            }

    @api.onchange('leave_date')
    def change_leave_date(self):

        self.leave_ss_date = self.leave_date

    @api.onchange('employee_id')
    def change_employee_id(self):

        self.current_company_id = self.employee_id.company_id.id