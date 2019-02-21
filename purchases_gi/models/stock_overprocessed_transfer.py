# -*- coding: utf-8 -*-
# © <2016> <Juan Carlos Vazquez Beas (jcvazquez@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api

class stock_overprocessed_transfer(models.TransientModel):
    _inherit = 'stock.overprocessed.transfer'

    def create_inputs(self):
        self.ensure_one()
        acom = []
        aux = 0
        order_id = None
        for line_id in self.picking_id.move_lines:
            if line_id.quantity_done > 0.0:
        

                order_id = self.env['purchase.order'].sudo().search([('name', '=', self.picking_id.origin)], limit=1)
                if order_id:
                    for move_lines_id in line_id.move_line_ids:
                        reception_id = self.env['purchase.reception'].create({'product_id': line_id.product_id.id, 'order_id': order_id.id, 'qty': move_lines_id.qty_done, 'get_qty': move_lines_id.qty_done, 'state': 'received','date_request': fields.Date.today(), 'company_id':self.picking_id.company_id.id, 'picking_id':self.picking_id.id, 'purchase_line_id': line_id.purchase_line_id.id})

                        folio_sequence = self.env['ir.sequence'].sudo().search([('name', '=', 'reception'),('company_id','=', self.picking_id.company_id.id)], limit=1)

                        if not folio_sequence:
                            raise ValidationError('No está configurada una secuencia "Orden de compra" para la compañía.')
                        reception_id.name = folio_sequence._next()

                        #Busca todas las lineas y les agrega el lote que será el mismo que el numero de entrada

                        move_lines_id.lot_name = reception_id.name
                        acom.append(reception_id.name)
                        aux = aux + 1

        return self.picking_id.with_context(skip_overprocessed_check=True).button_validate()