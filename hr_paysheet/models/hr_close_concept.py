# -*- coding: utf-8 -*-
# © <2016> <Omar Torres Silva (otorres@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api

class hr_close_concept(models.Model):
    _name = 'hr.close.concept'
    _description = 'HR CLOSE CONCEPT'

    name = fields.Char(
        string='Nombre'
    )
    concept_id = fields.Many2one(
        string='Concepto',
        comodel_name='hr.paysheet.concept'
    )
    year_id = fields.Many2one(
        string='Ejercicio',
        comodel_name='hr.paysheet.year'
    )
    lot_id = fields.Many2one(
        string='Lote',
        comodel_name='hr.paysheet.lot'
    )

    @api.model
    def create(self, vals):
        rec = super(hr_close_concept, self).create(vals)

        rec.sudo().write({
            'name': 'CL-%s' % str(rec.id).zfill(6),
            'year_id': rec.lot_id.year_id.id
        })

        return rec
