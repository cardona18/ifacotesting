# -*- coding: utf-8 -*-
# © <2016> <Omar Torres Silva (otorres@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime
import logging

from openerp import fields, models, api

_logger = logging.getLogger(__name__)

class hr_sdi_calc(models.TransientModel):
    _name = 'hr.sdi.calc'
    _description = 'HR SDI CALC'

    def _default_iterval(self):

        current_date = datetime.today()
        default_month = (current_date.month / 2 if current_date.month % 2 == 0 else (current_date.month + 1) / 2) - (1 if current_date.month > 1 else -5)
        return str(default_month if default_month > 0 else 6)


    interval = fields.Selection(
        string='Bimestre',
        size=1,
        default=_default_iterval,
        selection=[
            ('1', 'Enero - Febrero'),
            ('2', 'Marzo - Abril'),
            ('3', 'Mayo - Junio'),
            ('4', 'Julio - Agosto'),
            ('5', 'Septiembre - Octubre'),
            ('6', 'Noviembre - Diciembre')
        ]
    )
    employee_ids = fields.Many2many(
        string='Empleados',
        comodel_name='hr.employee'
    )
    preview_ids = fields.One2many(
        string='Resultados',
        comodel_name='hr.sdi.result',
        inverse_name='wizard_id'
    )
    change_date = fields.Date(
        string='Fecha'
    )
    state = fields.Selection(
        string='Estado',
        default='SEL',
        selection=[
            ('SEL', 'Selección'),
            ('REV', 'Revisión')
        ]
    )

    @api.multi
    def sdi_calc(self):

        contracts = self.env['hr.contract'].search([
            ('employee_id', 'in', [employee.id for employee in self.employee_ids]),
            ('for_paysheet', '=', True)
        ])

        for contract in contracts:
            res = contract.sdi_calc(int(self.interval) - 1 if int(self.interval) > 1 else int(self.interval))

            self.env['hr.sdi.result'].create({
                'contract_id': contract.id,
                'wizard_id': self.id,
                'sdi': res['sdi'],
                'days': res['natural_days'],
                'pantry': res['pantry_sum'],
                'holidays': res['dh_wage'],
                'xmas_bonus': res['xb_wage'],
                'var_income': res['var_income']
            })

        self.state = 'REV'

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'hr.sdi.calc',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }

    @api.multi
    def sdi_save(self):

        for prev in self.preview_ids:

            if round(prev.contract_id.sdi, 2) == round(prev.sdi, 2):
                continue

            sc_values = {
                'contract_id': prev.contract_id.id,
                'old_salary': prev.contract_id.wage,
                'old_sdi': prev.contract_id.sdi,
                'move_date': self.change_date
            }

            if prev.contract_id.sdi > 0:

                prev.contract_id.sdi = prev.sdi

                sc_values['new_sdi'] = prev.contract_id.sdi
                sc_values['new_salary'] = prev.contract_id.wage

                self.env['hr.salary.change'].create(sc_values)

            else:

                prev.contract_id.sdi = prev.sdi
