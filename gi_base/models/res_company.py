# -*- coding: utf-8 -*-
# © <2016> <Omar Torres Silva (otorres@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models

class res_company(models.Model):
    _inherit = 'res.company'

    short_name = fields.Char(
        string='Nombre corto',
        size=20
    )
    is_lab = fields.Boolean(
        string='Es laboratorio'
    )
    ced_emp = fields.Char(
        string='Ced. empadronamineto',
        size=12
    )
    reg_camara = fields.Char(
        string='Reg. camara canifar',
        size=12
    )
    secofi = fields.Char(
        string='Padrón SECOFI',
        size=20
    )
    ppapf = fields.Char(
        string='P.P.A.P.F.',
        size=15
    )