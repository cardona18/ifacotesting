# -*- coding: utf-8 -*-
# © <2016> <Omar Torres Silva (otorres@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime
from dateutil import tz

from openerp import fields, models, api

class hr_salary_change_wizard(models.TransientModel):
    _name = 'hr.salary.change.wizard'
    _description = 'HR SALARY CHANGE WIZARD'

    change_type = fields.Selection(
        string='Tipo',
        selection=[
            ('VAL', 'Cantidad'),
            ('PER', 'Porcentaje')
        ]
    )
    amount = fields.Float(
        string='Cantidad',
        digits=(16, 2)
    )
    percent = fields.Float(
        string='Porcentaje',
        digits=(16, 2)
    )
    contract_ids = fields.Many2many(
        string='Contratos',
        comodel_name='hr.contract',
        domain="[('for_paysheet', '=', True)]"
    )
    change_date = fields.Date(
        string='Fecha',
        default=datetime.today()
    )

    @api.one
    def change_wages(self):
        """
            Change contract wages
        """

        for contract_id in self.contract_ids:

            sc_values = {
                'contract_id': contract_id.id,
                'old_salary': contract_id.wage,
                'old_sdi': contract_id.sdi,
                'move_date': self.change_date
            }

            if(self.change_type == 'VAL'):

                contract_id.sudo().wage += self.amount

                res = contract_id.sdi_calc()
                contract_id.sudo().sdi = res['sdi']

                sc_values['new_sdi'] = contract_id.sudo().sdi
                sc_values['new_salary'] = contract_id.sudo().wage

                self.env['hr.salary.change'].create(sc_values)

                continue

            if(self.change_type == 'PER'):

                percent_amount = round(contract_id.sudo().wage * self.percent / 100)

                contract_id.sudo().wage += percent_amount

                res = contract_id.sdi_calc()
                contract_id.sudo().sdi = res['sdi']

                sc_values['new_sdi'] = contract_id.sudo().sdi
                sc_values['new_salary'] = contract_id.sudo().wage

                self.env['hr.salary.change'].create(sc_values)

    def _utc_to_tz(self, _date, _time_zone):

        # CONVER TO UTC
        _date = _date.replace(tzinfo = tz.gettz('UTC'))

        # LOAD TIMEZONE
        to_zone  = tz.gettz(_time_zone)

        return _date.astimezone(to_zone)