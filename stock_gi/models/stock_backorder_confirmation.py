# -*- coding: utf-8 -*-
# © <2016> <Juan Carlos Vazquez Beas (jcvazquez@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from odoo import fields, models, api
from odoo.exceptions import UserError
from openerp.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class stock_backorder_confirmation_gi(models.TransientModel):
    _inherit = 'stock.backorder.confirmation'
    

    @api.multi
    def process_backorder_gi(self):
        """
        Crea la entrada cuando es una parcialidad y llama a la función 'process' de odoo
        """
        acom = []
        aux = 0
        order_id = None
        for line_id in self.pick_ids.move_lines:
            if line_id.quantity_done > 0.0:


                for move_id in line_id.move_line_ids:
                    
                    if move_id.lot_name == 'Borrador' and self.pick_ids.operation_type == 'incoming':
                        order_id = self.env['purchase.order'].sudo().search([('name', '=', self.pick_ids.origin)], limit=1)

                        if order_id:
                            reception_id = self.env['purchase.reception'].create({'product_id': move_id.product_id.id, 'order_id': order_id.id, 'qty': move_id.qty_done, 'get_qty': move_id.qty_done, 'state': 'received','date_request': fields.Date.today(),'company_id': self.pick_ids.company_id.id, 'picking_id':self.pick_ids.id, 'purchase_line_id': line_id.purchase_line_id.id})

                            folio_sequence = self.env['ir.sequence'].sudo().search([('name', '=', 'reception'),('company_id','=', self.pick_ids.company_id.id)], limit=1)

                            if not folio_sequence:
                                raise ValidationError('No está configurada una secuencia "Orden de compra" para la compañía.')
                            reception_id.name = folio_sequence._next()

                            #Agrega el lote que será el mismo que el numero de entrada.
                            move_id.lot_name = reception_id.name
                            acom.append(reception_id.name)
                            aux = aux + 1
        aux = 0

        for acom_name in acom:
            lot_id = self.env['stock.production.lot'].sudo().search([('name', '=', acom_name)], limit=1)
            if lot_id:
                lot_id.partner_id = order_id.partner_id.id
            aux = aux + 1

        self.process()



    @api.multi
    def process_cancel_backorder_gi(self):
        """
        Crea la entrada cuando es una parcialidad y se cancela el restante llama a la función 'process' de odoo
        """
        acom = []
        aux = 0
        order_id = None
        for line_id in self.pick_ids.move_lines:
            if line_id.quantity_done > 0.0:

                for move_id in line_id.move_line_ids:
                    order_id = self.env['purchase.order'].sudo().search([('name', '=', self.pick_ids.origin)], limit=1)

                    if order_id:
                        reception_id = self.env['purchase.reception'].create({'product_id': move_id.product_id.id, 'order_id': order_id.id, 'qty': move_id.qty_done, 'get_qty': move_id.qty_done, 'state': 'received','date_request': fields.Date.today(),'company_id': self.pick_ids.company_id.id, 'purchase_line_id': line_id.purchase_line_id.id})

                        folio_sequence = self.env['ir.sequence'].sudo().search([('name', '=', 'reception'),('company_id','=', self.pick_ids.company_id.id)], limit=1)

                        if not folio_sequence:
                            raise ValidationError('No está configurada una secuencia "Orden de compra" para la compañía.')
                        reception_id.name = folio_sequence._next()

                        #Busca todas las lineas y les agrega el lote que será el mismo que el numero de entrada
                        move_id.lot_name = reception_id.name
                        acom.append(reception_id.name)
                        aux = aux + 1

        aux = 0

        for acom_name in acom:

            lot_id = self.env['stock.production.lot'].sudo().search([('name', '=', acom_name)], limit=1)
            if lot_id:
                lot_id.partner_id = order_id.partner_id.id
            aux = aux + 1

        self.process_cancel_backorder()
