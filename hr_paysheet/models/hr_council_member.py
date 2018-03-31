# -*- coding: utf-8 -*-
# © <2016> <Omar Torres Silva (otorres@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models

class hr_council_member(models.Model):
    _name = 'hr.council.member'
    _description = 'HR COUNCIL MEMBER'

    name = fields.Char(
        string='Nombre',
        required=True
    )
    rfc = fields.Char(
        string='RFC',
        required=True
    )
    zip_code = fields.Char(
        string='Código postal',
        size=5,
        required=True,
        help="Código postal del lugar donde se emite el pago."
    )
    work_state_id = fields.Many2one(
        string='Lugar de trabajo',
        comodel_name='res.country.state',
        help="""Último estado donde trabajó el periodo de nómina,
en caso de haber trabajado en varios estados
indicar el estado donde trabajó mas tiempo."""
    )
    period = fields.Selection(
        string='Periodicidad de pago',
        required=True,
        size=10,
        selection=[
            ('01', 'Diario'),
            ('02', 'Semanal'),
            ('03', 'Catorcenal'),
            ('04', 'Quincenal'),
            ('05', 'Mensual'),
            ('06', 'Bimestral'),
            ('07', 'Unidad obra'),
            ('08', 'Comisión'),
            ('09', 'Precio alzado'),
            ('99', 'Otra Periodicidad')
        ]
    )
    contract_type_id = fields.Many2one(
        string='Tipo de contrato',
        comodel_name='hr.contract.type'
    )
    curp = fields.Char(
        string='CURP',
        required=True
    )
    regime_id = fields.Many2one(
        string='Regimen de contratación',
        comodel_name='hr.contract.regime'
    )
    state_tax = fields.Float(
        string='% Impuesto Estatal',
        digits=(16,2),
        default=0.04
    )
    payment_ids = fields.One2many(
        string='Pagos',
        comodel_name='hr.council.payment',
        inverse_name='member_id'
    )