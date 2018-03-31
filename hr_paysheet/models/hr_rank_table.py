# -*- coding: utf-8 -*-
# © <2016> <Omar Torres Silva (otorres@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models

class hr_rank_table(models.Model):
    _name = 'hr.rank.table'
    _description = 'HR RANK TABLE'

    name = fields.Char(
        string='Nombre',
        required=True
    )
    code = fields.Char(
        string='Clave',
        required=True
    )
    rows_count = fields.Integer(
        string='Filas',
        compute='_rows_count',
    )
    row_ids = fields.One2many(
        string='Filas',
        comodel_name='hr.rank.row',
        inverse_name='table_id'
    )

    def _rows_count(self):
        """
        Count all hr.rank.row related records
        """

        self.rows_count = self.row_ids.search_count([('table_id', '=', self.id)])

    def find_value(self, table_code, value):
        """
        Find value in hr.rank.table by code

        @param table_code (str): code to find table
        @param value (float): value to find in rows

        @return hr.rank.row (obj): return hr.rank.row object if its found else return False
        """

        table = self.sudo().search([('code', '=', table_code)], limit=1)

        if(not table.id):

            return False

        for row in table.sudo().row_ids:

            if((value >= row.min_limit) and (value <= row.max_limit)):

                return row

        return False

    def self_find(self, value):
        """
        Find value in self hr.rank.table

        @param value (float): value to find in rows

        @return hr.rank.row (obj): return hr.rank.row object if its found else return False
        """

        for row in self.row_ids:

            if (value >= row.min_limit) and (value <= row.max_limit):

                return row

        return False



