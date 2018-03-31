# -*- coding: utf-8 -*-
# © <2016> <Omar Torres Silva (otorres@grupoifaco.com.mx) >
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models

class hr_paysheet_concept(models.Model):
    _name = 'hr.paysheet.concept'
    _description = 'Paysheet concept'
    _order = 'code'

    name = fields.Char(
        string='Name',
        required=True,
        size=80
    )
    active = fields.Boolean(
        string='Activo',
        default=True
    )
    code = fields.Integer(
        string='Clave',
        required=True
    )
    is_benefit = fields.Boolean(
        string='Es prestación'
    )
    ctype = fields.Selection(
        string='Tipo',
        size=3,
        selection=[
            ('PER', 'Percepción'),
            ('DED', 'Deducción'),
            ('EST', 'Estadistico'),
            ('REF', 'Referencia')
        ]
    )
    other_payments = fields.Boolean(
        string='Otros Pagos'
    )
    other_payments_type = fields.Selection(
        string='Tipo de Otros Pagos',
        size=3,
        help="""001 Reintegro de ISR pagado en exceso (siempre que no haya sido enterado al SAT).
002 Subsidio para el empleo (efectivamente entregado al trabajador).
003 Viáticos (entregados al trabajador).
004 Aplicación de saldo a favor por compensación anual.
999 Pagos distintos a los listados y que no deben considerarse como ingreso por sueldos, salarios o ingresos asimilados.""",
        selection=[
            ('001', '001 - Reintegro de ISR'),
            ('002', '002 - Subsidio para el empleo'),
            ('003', '003 - Viáticos'),
            ('004', '004 - Saldo a favor por compensación anual'),
            ('999', '999 - Distinto a sueldos, salarios o ingresos asimilados')
        ]
    )
    printable = fields.Boolean(
        string='Se imprime en recibo'
    )
    report_print = fields.Boolean(
        string='Se imprime en reporte'
    )
    free_concept_id = fields.Many2one(
        string='Concepto exento',
        comodel_name='hr.paysheet.concept'
    )
    tax_concept_id = fields.Many2one(
        string='Concepto gravable',
        comodel_name='hr.paysheet.concept'
    )
    sat_concept_id = fields.Many2one(
        string='Concepto SAT',
        comodel_name='hr.paysheet.sat.concept'
    )
    sdi_integration = fields.Selection(
        string='Integración al salario',
        help='Tipo de integración al salario, vacio no se integra',
        selection=[
            ('UNL', 'Sin limite'),
            ('LIM', 'Limitado')
        ]
    )
    config_ids = fields.One2many(
        string='Configuración',
        comodel_name='hr.policy.config',
        inverse_name='concept_id'
    )
    old_conf_ids = fields.One2many(
        string='Configuración',
        comodel_name='hr.old.policy.conf',
        inverse_name='concept_id'
    )
    pantry_card = fields.Boolean(
        string='Pago en vales',
        help="Se paga por medio de vales o efectivo"
    )