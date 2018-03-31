# -*- coding: utf-8 -*-
# © <2016> <Omar Torres Silva (otorres@grupoifaco.com.mx) >
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models

class hr_paysheet_struct(models.Model):
    _name = 'hr.paysheet.struct'
    _description = 'Paysheet struct'

    name = fields.Char(
        string='Nombre',
        required=True,
        size=64
    )
    period = fields.Selection(
        string='Periodicidad',
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
    stype = fields.Selection(
        string='Tipo',
        required=True,
        size=1,
        default='O',
        selection=[
            ('O', 'Nómina ordinaria'),
            ('E', 'Nómina extraordinaria')
        ]
    )
    internal_type = fields.Selection(
        string='Tipo interno',
        required=True,
        size=1,
        default='S',
        selection=[
            ('S', 'Semanal'),
            ('M', 'Mensual'),
            ('E', 'Especial'),
            ('F', 'Finiquito')
        ]
    )
    rule_ids = fields.Many2many(
        string='Reglas',
        comodel_name='hr.paysheet.rule',
        domain=[('vtype', '=', 'L')]
    )