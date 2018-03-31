# -*- coding: utf-8 -*-
# © <2017> <Omar Torres Silva (otorres@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models

class ireport_fixed_image(models.Model):
    _name = 'ireport.fixed.image'
    _description = 'IREPORT FIXED IMAGE'

    report_id = fields.Many2one(
        string='Reporte',
        comodel_name='ireport.report'
    )
    parameter = fields.Char(
        string='Parametro de la ruta',
        size=50
    )
    image = fields.Binary(
        string='Imagen'
    )
    imagename = fields.Char(
        string='Imagen (nombre)'
    )
