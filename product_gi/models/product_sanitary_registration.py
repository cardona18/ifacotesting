# -*- coding: utf-8 -*-
# © <2017> <Omar Torres Silva (otorres@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models

class product_sanitary_registration(models.Model):
    _name = 'product.sanitary.registration'
    _description = 'PRODUCT SANITARY REGISTRATION'

    name = fields.Char(
        string='Registro',
        required=True
    )
    description_code = fields.Char(
        string='Denominación distintiva'
    )
    gen_description = fields.Char(
        string='Denominación genérica'
    )
    group_lgsa226_id = fields.Many2one(
        string='Fracción',
        comodel_name='product.lgsa226'
    )
    form_id = fields.Many2one(
        string='Forma farmacéutica',
        comodel_name='product.pharm.form'
    )
    expiration_months = fields.Integer(
        string='Vida útil (meses)'
    )
    expedition_date = fields.Date(
        string='Fecha de expedición'
    )
    expiration_date = fields.Date(
        string='Fecha de vencimiento'
    )
    extension_date = fields.Date(
        string='Fecha de prorroga'
    )
    partner_maker_id = fields.Many2one(
        string='Fabricante del fármaco',
        comodel_name='res.partner'
    )
    therapy_instruction = fields.Char(
        string='Indicación terapeutica'
    )
    contraindication = fields.Text(
        string='Contraindicaciones'
    )
    admin_form = fields.Char(
        string='Vía de administración'
    )
    use_considerations = fields.Char(
        string='Consideraciones de uso'
    )
    has_thinner = fields.Char(
        string='Tiene diluyente'
    )
    exchange_test = fields.Char(
        string='Prueba de Intercambiabilidad'
    )
    update_tag_date = fields.Date(
        string='Actualización de marbete'
    )
    update_ipps_date = fields.Date(
        string='Actualización de IPPs'
    )