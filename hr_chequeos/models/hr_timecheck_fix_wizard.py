# -*- coding: utf-8 -*-
# © <2017> <Omar Torres Silva (otorresgi18@gmail.com)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api

class hr_timecheck_fix_wizard(models.TransientModel):
    _name = 'hr.timecheck.fix.wizard'
    _description = 'HR TIMECHECK FIX WIZARD'

    workday_id = fields.Many2one(
        string='Día',
        comodel_name='hr.timecheck.workday'
    )
    ctype = fields.Selection(
        string='Acción',
        size=1,
        default='A',
        selection=[
            ('A', 'Agregar'),
            ('M', 'Modificar'),
            ('D', 'Eliminar'),
            ('C', 'Solo completar')
        ]
    )
    complete = fields.Boolean(
        string='Completar',
        default=False
    )
    complete_number = fields.Integer(
        string='Número'
    )
    new_time = fields.Datetime(
        string='Hora'
    )
    del_codes = fields.Char(
        string='Números',
        help="Número(s) de checada separados por coma"
    )

    @api.multi
    def fix_workday(self):

        log_text = False

        if self.ctype == 'A':

            self.env['hr.timecheck'].create({
                'workday_id': self.workday_id.id,
                'name': self.complete_number,
                'check_time': self.new_time
            })

            log_text  = "Creación: %s" % self.new_time

        if self.ctype == 'M':

            timecheck_id = self.env['hr.timecheck'].search([('workday_id', '=', self.workday_id.id), ('name', '=', self.complete_number)], limit=1)

            if timecheck_id.id:

                log_text  = "Modificación:\n"
                log_text += "%s => %s\n" % (timecheck_id.check_time, self.new_time)

                timecheck_id.write({
                    'check_time': self.new_time
                })

        if self.ctype == 'D':

            numbers = [code for code in self.del_codes.split(',')]
            delete_ids = self.env['hr.timecheck'].search([('workday_id', '=', self.workday_id.id), ('name', 'in', numbers)])

            log_text  = "Eliminado(s):\n"

            for del_id in delete_ids:
                log_text += "%s -- %s -- %s\n" % (self.workday_id.name, del_id.name, del_id.check_time)

            delete_ids.unlink()

        if self.complete or self.ctype == 'C':
            log_text = "%sCompletada: %s" % (log_text, self.workday_id.name) if log_text else "Completada: %s" % self.workday_id.name
            self.workday_id.is_complete = True

        if log_text:

            self.env['hr.timefix.log'].create({
                'employee_id': self.workday_id.employee_id.id,
                'log_detail': log_text
            })