# -*- coding: utf-8 -*-
# © <2016> <Omar Torres Silva (otorres@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api

class hr_periodic_payment(models.Model):
    _name = 'hr.periodic.payment'
    _description = 'HR PERIODIC PAYMENT'

    _sql_constraints = [
        ('unique_payment', 'unique(employee_id, concept_id, mtype)', 'Ya se registró un movimiento igual')
    ]

    name = fields.Char(
        string='Nombre'
    )
    employee_id = fields.Many2one(
        string='Empleado',
        comodel_name='hr.employee',
        required=True,
        ondelete='cascade'
    )
    company_id = fields.Many2one(
        string='Empresa',
        comodel_name='res.company',
        related='employee_id.company_id'
    )
    concept_id = fields.Many2one(
        string='Concepto',
        comodel_name='hr.paysheet.concept',
        ondelete='cascade',
        required=True,
    )
    mtype = fields.Selection(
        string='Tipo de movimiento',
        size=10,
        required=True,
        default='ONE_DATE',
        selection=[
            ('ONE_DATE', 'Aplicar por fecha'),
            ('AMOUNT', 'Aplicar hasta un limite'),
            ('DATE', 'Aplicar hasta una fecha'),
            ('UNL', 'Aplicar sin limite')
        ]
    )
    amount = fields.Float(
        string='Cantidad',
        digits=(16, 2)
    )
    amount_start = fields.Float(
        string='Cantidad inicial',
        digits=(16, 2)
    )
    current_amount = fields.Float(
        string='Cantidad actual',
        digits=(16, 2)
    )
    amount_limit = fields.Float(
        string='Limite',
        digits=(16, 2)
    )
    stop_date = fields.Date(
        string='Hasta'
    )
    struct_id = fields.Many2one(
        string='Estructura',
        comodel_name='hr.paysheet.struct'
    )
    apply_date = fields.Date(
        string='Fecha'
    )
    is_readonly = fields.Boolean(
        string='Solo lectura'
    )
    account1_id = fields.Many2one(
        string='Cuenta',
        comodel_name='hr.policy.line'
    )
    account2_id = fields.Many2one(
        string='Contra cuenta',
        comodel_name='hr.policy.line'
    )
    paid = fields.Boolean(
        string='Pagado'
    )


    @api.model
    def create(self, vals):
        rec = super(hr_periodic_payment, self).create(vals)

        rec.sudo().write({
            'name': '%s/%s' % (rec.employee_id.company_id.short_name, str(rec.employee_id.old_id).zfill(4))
        })

        return rec

    def find_payment(self, code, employee_id):

        concept_id = self.env['hr.paysheet.concept'].search([
            ('code', '=', code)
        ], limit=1)

        return self.env['hr.periodic.payment'].search([
            ('concept_id', '=', concept_id.id),
            ('employee_id', '=', employee_id)
        ], limit=1) if concept_id.id else False