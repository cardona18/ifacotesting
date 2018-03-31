# -*- coding: utf-8 -*-
# © <2016> <Omar Torres Silva (otorres@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api
from openerp import tools

class hr_paysheet_report(models.Model):
    _name = "hr.paysheet.report"
    _description = "HR PAYSHEET REPORT"
    _auto = False


    employee_name = fields.Char(
        string='Empleado'
    )
    amount = fields.Float(
        string='Cantidad'
    )
    concept_id = fields.Many2one(
        string='Concepto',
        comodel_name='hr.paysheet.concept'
    )
    employer_id = fields.Many2one(
        string='Registro patronal',
        comodel_name='hr.employer.registration'
    )
    account_date = fields.Date(
        string='Fecha contable'
    )
    lot_state = fields.Selection(
        string='Estado',
        size=10,
        selection=[
            ('draft', 'Generado'),
            ('locked', 'Acumulado'),
            ('signed', 'Timbrado'),
            ('closed', 'Cerrado')
        ]
    )
    ltype = fields.Selection(
        string='Tipo lote',
        size=2,
        selection=[
            ('NO', 'Normal'),
            ('ES', 'Especial')
        ]
    )
    department_id = fields.Many2one(
        string='Departamento',
        comodel_name='hr.department'
    )
    segment_id = fields.Many2one(
        string='Segmento de negocio',
        comodel_name='hr.business.segment'
    )
    cost_center_id = fields.Many2one(
        string='Gasto contable',
        comodel_name='hr.account.expense'
    )
    company_id = fields.Many2one(
        string='Empresa',
        comodel_name='res.company'
    )
    ctype = fields.Selection(
        string='Tipo concepto',
        size=3,
        selection=[
            ('PER', 'Percepción'),
            ('DED', 'Deducción'),
            ('EST', 'Estadistico'),
            ('REF', 'Referencia')
        ]
    )
    month_id = fields.Many2one(
        string='Periodo',
        comodel_name='hr.paysheet.month'
    )
    year_id = fields.Many2one(
        string='Ejercicio',
        comodel_name='hr.paysheet.year'
    )

    @api.model_cr
    def init(self):
        """Initialize the sql view"""
        tools.drop_view_if_exists(self._cr, 'hr_paysheet_report')

        self._cr.execute(""" CREATE OR REPLACE VIEW hr_paysheet_report AS (
            SELECT
                pt.id AS id,
                em.name_related || ' (' || rc.short_name || '/' || lpad(em.old_id::varchar, 4, '0') || ') ' AS employee_name,
                sum(abs(pt.amount)) AS amount,
                psl.payment_date AS account_date,
                psl.state AS lot_state,
                psl.ltype AS ltype,
                pt.concept_id AS concept_id,
                em.department_id AS department_id,
                em.segment_id AS segment_id,
                em.expense_id AS cost_center_id,
                em.employer_registration AS employer_id,
                rr.company_id AS company_id,
                pc.ctype AS ctype,
                pt.year_id,
                psm.id AS month_id

            FROM
                hr_paysheet_trade pt
                INNER JOIN hr_paysheet ps ON pt.paysheet_id = ps.id
                INNER JOIN hr_paysheet_lot psl ON ps.lot_id = psl.id
                INNER JOIN hr_paysheet_month psm ON psl.period_id = psm.id
                INNER JOIN hr_employee em ON ps.employee_id = em.id
                INNER JOIN resource_resource rr ON em.resource_id = rr.id
                INNER JOIN res_company rc ON rr.company_id = rc.id
                INNER JOIN hr_paysheet_concept pc ON pt.concept_id = pc.id

            GROUP BY
                pt.id,
                employee_name,
                concept_id,
                department_id,
                segment_id,
                cost_center_id,
                employer_id,
                rr.company_id,
                account_date,
                lot_state,
                ltype,
                pc.ctype,
                pt.year_id,
                month_id
        )
        """)

