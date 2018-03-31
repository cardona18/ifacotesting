# -*- coding: utf-8 -*-
# © <2016> <Omar Torres Silva (otorres@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api
from openerp import tools

class hr_wage_report(models.Model):
    _name = "hr.wage.report"
    _description = "HR WAGE REPORT"
    _auto = False

    name = fields.Char(
        string='Empleado'
    )
    wage = fields.Float(
        string='Salario base'
    )
    sbc = fields.Float(
        string='SBC'
    )
    sdii = fields.Float(
        string='SDI (Interno)'
    )
    area_id = fields.Many2one(
        string='Área',
        comodel_name='hr.department'
    )
    department_id = fields.Many2one(
        string='Departamento',
        comodel_name='hr.department'
    )
    academic_level_id = fields.Many2one(
        string='Nivel académico',
        comodel_name='hr.academic.level'
    )
    profession_id = fields.Many2one(
        string='Profesión',
        comodel_name='hr.profession'
    )
    company_id = fields.Many2one(
        string='Empresa',
        comodel_name='res.company'
    )

    @api.model_cr
    def init(self):
        """Initialize the sql view"""
        tools.drop_view_if_exists(self._cr, 'hr_wage_report')

        self._cr.execute(""" CREATE VIEW hr_wage_report AS (
            SELECT

            rc_id + he_id AS id,
            tq.*,
            (( (sbm + ab_month + pantry + holidays_bonus + xb_month + ptu_month + sf_month + work_bonus + sq_insurance + year_bonus_one) * 12 ) / 365 )::numeric(18,2) AS sdii

            FROM (

                SELECT

                sq.*,
                COALESCE(round((sq.ant_bonus_days * ( wage + (pantry * 12) / 365 )) / 12), 0) AS year_bonus_one,
                COALESCE(sq.ant_bonus_days * ( wage + (pantry * 12) / 365 ), 0)::numeric(18,2) AS year_bonus

                FROM (

                    SELECT

                        fq.*,
                        (((((fq.pantry * 12) / 365) + fq.wage) * xmas_bonus) / 12)::numeric(18,2) AS xb_month,
                        (((fq.wage * fq.holidays) * 0.25 ) / 12)::numeric(18,2) AS holidays_bonus,
                        (((((fq.pantry * 12) / 365) + fq.wage) * ptu_days) / 12)::numeric(18,2) AS ptu_month,
                        ((( fq.wage * (savings_fund / 100) ) * 365) / 12)::numeric(18,2) AS sf_month,
                        ((( fq.wage * (ant_bonus / 100) ) * 365) / 12)::numeric(18,2) ab_month,
                        round(fq.insurance / 12) AS sq_insurance,
                        CASE
                            WHEN fq.academic_bonus THEN (SELECT days FROM hr_year_bonus WHERE profession = TRUE AND years <= antique_years ORDER BY years DESC LIMIT 1)
                            WHEN fq.antique_years >= 10 AND NOT fq.academic_bonus THEN (SELECT days FROM hr_year_bonus WHERE years <= antique_years ORDER BY years DESC LIMIT 1)
                            ELSE 0
                        END
                        AS ant_bonus_days

                    FROM (

                        SELECT

                        he.resource_id AS rc_id,
                        he.id AS he_id,
                        he.name_related || ' (' || rc.short_name || '/' || lpad(he.old_id::varchar, 4, '0') || ') ' AS name,
                        find_department_id(he.department_id) AS department_id,
                        he.department_id AS area_id,
                        he.job_id,
                        rr.company_id,
                        he.academic_level_id,
                        he.profession_id,
                        EXTRACT(year FROM age(he.in_date)) AS antique_years,
                        COALESCE(hal.antique_bonus, FALSE) AS academic_bonus,
                        hc.wage AS wage,
                        hc.sdi AS sbc,
                        CASE
                            WHEN he.has_medical_insurance THEN he.medical_insurance
                            ELSE 0
                        END
                        AS insurance,
                        (
                            SELECT pb.amount
                            FROM hr_paysheet_benefit pb
                            INNER JOIN hr_paysheet_concept pbc ON pb.concept_id = pbc.id
                            WHERE pb.contract_id = hc.id AND pbc.code = 36
                        ) AS holidays,
                        (
                            SELECT pb.amount
                            FROM hr_paysheet_benefit pb
                            INNER JOIN hr_paysheet_concept pbc ON pb.concept_id = pbc.id
                            WHERE pb.contract_id = hc.id AND pbc.code = 24
                        ) AS xmas_bonus,
                        COALESCE((
                            SELECT pb.amount
                            FROM hr_paysheet_benefit pb
                            INNER JOIN hr_paysheet_concept pbc ON pb.concept_id = pbc.id
                            WHERE pb.contract_id = hc.id AND pbc.code = 14
                        ),0) AS ptu_days,
                        COALESCE((
                            SELECT pb.amount
                            FROM hr_paysheet_benefit pb
                            INNER JOIN hr_paysheet_concept pbc ON pb.concept_id = pbc.id
                            WHERE pb.contract_id = hc.id AND pbc.code = 17
                        ),0) AS savings_fund,
                        COALESCE((
                            SELECT pb.amount
                            FROM hr_paysheet_benefit pb
                            INNER JOIN hr_paysheet_concept pbc ON pb.concept_id = pbc.id
                            WHERE pb.contract_id = hc.id AND pbc.code = 81
                        ),0) AS ant_bonus,
                        (hc.wage * 365 / 12)::numeric(18,2) AS sbm,
                        COALESCE((
                            SELECT pb.amount
                            FROM hr_paysheet_benefit pb
                            INNER JOIN hr_paysheet_concept pbc ON pb.concept_id = pbc.id
                            WHERE pb.contract_id = hc.id AND pbc.code = 15
                        ),0) AS pantry,
                        COALESCE((
                            SELECT pb.amount
                            FROM hr_paysheet_benefit pb
                            INNER JOIN hr_paysheet_concept pbc ON pb.concept_id = pbc.id
                            WHERE pb.contract_id = hc.id AND pbc.code = 38
                        ), 0) AS work_bonus

                        FROM hr_employee he

                        INNER JOIN resource_resource rr ON he.resource_id = rr.id
                        INNER JOIN res_company rc ON rr.company_id = rc.id
                        LEFT  JOIN hr_academic_level hal ON he.academic_level_id = hal.id
                        INNER JOIN hr_contract hc ON hc.employee_id = he.id AND hc.for_paysheet = TRUE AND hc.active = TRUE

                        WHERE rr.active = TRUE

                    ) AS fq

                ) AS sq

            ) AS tq
        )
        """)

