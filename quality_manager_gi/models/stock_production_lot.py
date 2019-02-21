# -*- coding: utf-8 -*-
# © <2016> <Juan Carlos Vazquez Beas (jcvazquez@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from odoo import fields, models, api
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class stock_production_lot(models.Model):
    _inherit = 'stock.production.lot'
    
    def get_res_partner(self):
        for rec in self:
            reception_id = rec.env['purchase.reception'].sudo().search([('name', '=', rec.name)], limit=1)
            if not rec.partner_id:
                if reception_id.order_id:
                    rec.partner_id = reception_id.order_id.partner_id.id


    def get_company_id(self):
        for rec in self:
            reception_id = rec.env['purchase.reception'].sudo().search([('name', '=', rec.name)], limit=1)
            if not rec.company_id:
                if reception_id.company_id:
                    rec.company_id = reception_id.company_id.id

    
    ref = fields.Char(
        string='Lote proveedor',
        track_visibility='onchange'
    )
    company_id = fields.Many2one(
        'res.company',
        string='Compañia',
        store=True,
        readonly=False, 
        compute=get_company_id
    )
    use_date = fields.Datetime(
        string='Consumir preferentemente antes de',
        track_visibility='onchange'
    )
    removal_date = fields.Datetime(
        string='Fecha de eliminación',
        track_visibility='onchange'
    )
    life_date = fields.Datetime(
        string='Fecha de vigencia',
        track_visibility='onchange'
    )
    make_date = fields.Date(
        string='Fecha de fabricación',
        track_visibility='onchange'        
    )
    alert_date = fields.Datetime(
        string='Fecha de alerta',
        track_visibility='onchange'        
    )
    container_num  = fields.Integer(
        string='Número de contenedores',
    )
    date_analysis = fields.Date(
        string='Fecha de análisis',
        track_visibility='onchange'        

    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Proveedor',
        store=True,
        readonly=False, 
        compute=get_res_partner
    )
    doc_number  = fields.Integer(
        string='Número de documento',
        size=20,
    )
    num_container = fields.Integer(
        string='Número de contenedores',
        default=1
    )
    employee_id = fields.Many2one(
        'hr.employee',
        string='Nombre del analista',
        domain=[('is_analysis','=',True), ]
    )
    valuation = fields.Float(
        string='Valoración',
        track_visibility='onchange'        
    )
    unit_valuation = fields.Selection(
        string='Unidad de valoración',
        size=5,
        selection=[
            ('ave', '%'),
            ('uimg', 'UI/mg'),
            ('mcg', 'mcg/mg'),
            ('uiml', 'UI/ml'),
        ],
        track_visibility='onchange'
    )

    type_product = fields.Selection(string='Tipo', related='product_id.type')

    @api.multi
    def write(self, vals):
 
        try:
            if vals['life_date']:
                vals['removal_date'] = vals['life_date']
                self.removal_date = vals['life_date']

        except Exception as e:
            pass


        return super(stock_production_lot, self).write(vals)