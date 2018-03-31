# -*- coding: utf-8 -*-
# © <2017> <Omar Torres Silva (otorresgi18@gmail.com)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from openerp import fields, models, api

_logger = logging.getLogger(__name__)

class hr_paysheet_lot_wizard(models.TransientModel):
    _name = 'hr.paysheet.lot.wizard'
    _description = 'HR PAYSHEET LOT WIZARD'

    gen_type = fields.Selection(
        string='Acción',
        default='GEN',
        size=3,
        selection=[
            ('GEN', 'Generar'),
            ('GEC', 'Generar y cálcular')
        ]
    )
    gen_include = fields.Selection(
        string='Tipo',
        default='LOT',
        size=3,
        selection=[
            ('LOT', 'Por lote'),
            ('EMP', 'Por empleado')
        ]
    )
    employee_ids = fields.Many2many(
        string='Empleados',
        comodel_name='hr.employee'
    )
    lot_ids = fields.Many2many(
        string='Lotes',
        comodel_name='hr.paysheet.lot'
    )
    replace_type = fields.Selection(
        string='Entradas',
        default='UPD',
        size=3,
        selection=[
            ('UPD', 'Actualizar'),
            ('REP', 'Remplazar')
        ]
    )
    gen_inactive = fields.Boolean(
        string='Empleados inactivos',
        default=False
    )
    gen_zero = fields.Boolean(
        string='Entradas en cero',
        default=False
    )
    gen_inputs = fields.Boolean(
        string='Generar entradas',
        default=True
    )

    @api.multi
    def generate_paysheets(self):

        for lot_id in self.lot_ids:

            employees_domain = [
                ('company_id', '=', lot_id.company_id.id)
            ]

            if self.gen_include == 'EMP':
                employees_domain.append(('id', 'in', [emp_id.id for emp_id in self.employee_ids]))

            if self.gen_inactive:
                employees_domain.append('|')
                employees_domain.append(('active', '=', True))
                employees_domain.append(('active', '=', False))

            for employee in self.env['hr.employee'].search(employees_domain):

                contract_domain = [
                    ('employee_id', '=', employee.id),
                    ('company_id', '=', lot_id.company_id.id),
                    ('for_paysheet', '=', True)
                ]

                if self.gen_inactive:
                    contract_domain.append('|')
                    contract_domain.append(('active', '=', True))
                    contract_domain.append(('active', '=', False))

                contract = self.env['hr.contract'].search(contract_domain, limit=1)

                if not contract.id:
                    _logger.warning('EMPLEADO SIN CONTRATO: %s' % employee.id)
                    continue

                if self.gen_inputs:

                    # DATE PAYMENTS

                    date_domain = [
                        ('employee_id', '=', employee.id),
                        ('mtype', '=', 'ONE_DATE'),
                        ('apply_date', '>=', lot_id.from_date),
                        ('apply_date', '<=', lot_id.to_date)
                    ]

                    if not self.gen_zero:
                        date_domain.append(('amount', '>', 0))

                    date_payments = self.env['hr.periodic.payment'].search(date_domain)

                    # PERIODIC PAYMENTS

                    payments_domain = [
                        ('employee_id', '=', employee.id),
                        ('mtype', '!=', 'ONE_DATE'),
                        ('paid', '=', False)
                    ]

                    if not self.gen_zero:
                        payments_domain.append(('amount', '>', 0))

                    payments_domain.append('|')
                    payments_domain.append(('struct_id', '=', lot_id.struct_id.id))
                    payments_domain.append(('struct_id', '=', False))

                    peridic_payments = self.env['hr.periodic.payment'].search(payments_domain)

                    all_payments = date_payments + peridic_payments

                    if len(all_payments) == 0 and not employee.active:
                        _logger.warning('EMPLEADO INACTIVO SIN ENTRADAS: %s' % employee.id)
                        continue

                else:
                    all_payments = []

                # GENERATE PAYSHEET

                paysheet_id = self.env['hr.paysheet'].search([
                    ('lot_id', '=', lot_id.id),
                    ('employee_id', '=', employee.id),
                    ('contract_id', '=', contract.id)
                ], limit=1)

                if not paysheet_id.id:

                    paysheet_id = self.env['hr.paysheet'].create({
                        'employee_id': employee.id,
                        'contract_id': contract.id,
                        'lot_id': lot_id.id
                    })

                if self.replace_type == 'REP' and self.gen_inputs:
                    paysheet_id.inputs_ids.unlink()

                for payment_id in all_payments:

                    if self.replace_type == 'UPD':

                        input_id = self.env['hr.paysheet.input'].search([
                            ('concept_id', '=', payment_id.concept_id.id),
                            ('paysheet_id', '=', paysheet_id.id)
                        ], limit=1)

                        if input_id.id:
                            input_id.amount = payment_id.amount
                            input_id.account1_id = payment_id.account1_id.id
                            input_id.account2_id = payment_id.account2_id.id
                            continue

                    self.env['hr.paysheet.input'].create({
                        'concept_id': payment_id.concept_id.id,
                        'amount': payment_id.amount,
                        'account1_id': payment_id.account1_id.id,
                        'account2_id': payment_id.account2_id.id,
                        'paysheet_id': paysheet_id.id,
                        'sys_input': True
                    })

                # COMPLETE WORKED DAYS INPUT

                if employee.has_check and self.gen_inputs:

                    wd_concept = self.env['hr.paysheet.concept'].search([
                        ('code', '=', 34)
                    ], limit=1)

                    wd_input_id = self.env['hr.paysheet.input'].search([
                        ('concept_id', '=', wd_concept.id),
                        ('paysheet_id', '=', paysheet_id.id)
                    ], limit=1)

                    if not wd_input_id.id:

                        self.env['hr.paysheet.input'].create({
                            'concept_id': wd_concept.id,
                            'amount': 6,
                            'paysheet_id': paysheet_id.id,
                            'sys_input': True
                        })

            if self.gen_type == 'GEC':
                lot_id.calculate_lot()
