# -*- coding: utf-8 -*-
# © <2016> <Omar Torres Silva (otorres@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api

class hr_ss_move(models.Model):
    _name = 'hr.ss.move'
    _description = 'HR SS MOVE'

    name = fields.Char(
        string='Nombre'
    )
    employee_id = fields.Many2one(
        string='Empleado',
        comodel_name='hr.employee',
        required=True
    )
    company_id = fields.Many2one(
        string='Empresa',
        comodel_name='res.company',
        related='employee_id.company_id'
    )
    inhability_type = fields.Selection(
        string='Tipo de Incidencia',
        selection=[
            ('1', '1 Riesgo de trabajo'),
            ('2', '2 Enfermedad General'),
            ('3', '3 Maternidad')
        ]
    )
    inhability_risk = fields.Selection(
        string='Tipo de Riesgo',
        selection=[
            ('1', '1 Accidente Trabajo'),
            ('2', '2 Accidente Trayecto'),
            ('3', '3 Enfermedad Profesional')
        ]
    )
    inhability_percent = fields.Integer(
        string='Porcentaje',
        help="""Digite, en su caso, el porcentaje de incapacidad anotado en el
Dictamen de Incapacidad Permanente o de Defunción por Riesgo de Trabajo expedido por el IMSS."""
    )
    implication = fields.Selection(
        string='Consecuencia',
        selection=[
            ('0', 'Ninguna'),
            ('1', 'Incap. Temporal'),
            ('2', 'Valuación inicial provisional'),
            ('3', 'Valuación inicial definitiva'),
            ('4', 'Defunción'),
            ('5', 'Recaída'),
            ('6', 'Valuación posterior a la fecha de alta'),
            ('7', 'Revaluación provisional'),
            ('8', 'Recaída sin alta médica'),
            ('9', 'Revaluación definitiva')
        ]
    )
    disease_control = fields.Selection(
        string='Control de la incapacidad',
        selection=[
            ('1', 'Única'),
            ('2', 'Inicial'),
            ('3', 'Subsecuente'),
            ('4', 'Alta médica o ST-2'),
        ]
    )
    implication_control = fields.Selection(
        string='Control de la incapacidad',
        selection=[
            ('1', 'Única'),
            ('2', 'Inicial'),
            ('3', 'Subsecuente'),
            ('4', 'Alta médica o ST-2'),
        ]
    )
    maternity_control = fields.Selection(
        string='Control de la incapacidad',
        selection=[
            ('7', 'Prenatal'),
            ('8', 'Enlace'),
            ('9', 'Postnatal')
        ]
    )
    single_control = fields.Selection(
        string='Control de la incapacidad',
        selection=[
            ('0', 'Ninguna'),
            ('5', 'Valuación o ST-3'),
            ('6', 'Defunción o ST-3')
        ]
    )
    inhability_file = fields.Binary(
        string='Comprobante'
    )
    inhability_fname = fields.Char(
        string='Archivo'
    )
    from_date = fields.Date(
        string='Desde'
    )
    to_date = fields.Date(
        string='Hasta'
    )
    folio = fields.Char(
        string='Folio'
    )

    @api.model
    def create(self, vals):
        rec = super(hr_ss_move, self).create(vals)

        rec.sudo().write({
            'name': '%s-%s' % (rec.employee_id.company_id.short_name, str(rec.employee_id.old_id).zfill(4))
        })

        return rec

    @api.onchange('implication')
    def implication_change(self):

        if self.implication == '0':
            self.single_control = '0'

        if self.implication in ('2','3','6','7','9'):
            self.single_control = '5'

        if self.implication == '4':
            self.single_control = '6'
