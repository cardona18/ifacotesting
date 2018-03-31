# -*- coding: utf-8 -*-
# © <2016> <Omar Torres Silva (otorres@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models

class hr_rank_row(models.Model):
    _name = 'hr.rank.row'
    _description = 'HR RANK ROW'

    def _default_name(self):

        last = self.search([], limit=1, order='id DESC')
        ret  = 1

        if(last.id):
            ret = int(last.name[4:]) + 1

        return 'ROW-' + str(ret)

    name = fields.Char(
        string='Nombre',
        default=_default_name,
        required=True
    )
    min_limit = fields.Float(
        string='Limite inferior',
        digits=(18,4)
    )
    max_limit = fields.Float(
        string='Limite superior',
        digits=(18,4)
    )
    fixed_amount = fields.Float(
        string='Cantidad fija'
    )
    extra_percent = fields.Float(
        string='Porcentaje excedente'
    )
    table_id = fields.Many2one(
        string='Tabla',
        comodel_name='hr.rank.table'
    )