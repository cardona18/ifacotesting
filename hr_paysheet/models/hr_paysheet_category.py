# -*- coding: utf-8 -*-
# © <2016> <Omar Torres Silva (otorres@grupoifaco.com.mx) >
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models

class hr_paysheet_category(models.Model):
    _name = 'hr.paysheet.category'
    _description = 'Paysheet category'

    name = fields.Char(
        string='Name',
        required=True,
        size=64
    )
    code = fields.Char(
        string='Codigo',
        required=True
    )
    concept_ids = fields.Many2many(
        string='Conceptos',
        comodel_name='hr.paysheet.concept'
    )

    def get_amount(self, code, paysheet_id):

        category = self.search([('code', '=', code)], limit=1)

        if not category.id:
            return 0

        cids = ','.join(str(concept.id) for concept in category.concept_ids)

        self.env.cr.execute("""
            SELECT COALESCE(SUM(ABS(amount)), 0)
            FROM hr_paysheet_trade pt
            WHERE pt.paysheet_id = %s
            AND pt.concept_id IN (%s)
        """ % (
            paysheet_id,
            cids
        ))

        amount = self.env.cr.fetchone()[0]

        self.env['hr.paysheet.rule'].update_value('categories', code, amount)

        return amount

    def amount_by_concepts(self, paysheet_id, concept_codes):

        codes = ','.join(str(code) for code in concept_codes)

        self.env.cr.execute("""
            SELECT COALESCE(SUM(ABS(amount)), 0)
            FROM hr_paysheet_trade pt
            INNER JOIN hr_paysheet_concept pc ON pt.concept_id = pc.id
            WHERE pt.paysheet_id = %s
            AND pc.code IN (%s)
        """ % (
            paysheet_id,
            codes
        ))

        return self.env.cr.fetchone()[0]