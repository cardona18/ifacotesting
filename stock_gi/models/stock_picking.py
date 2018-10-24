# -*- coding: utf-8 -*-
# © <2017> <Juan Carlos Vazquez Beas (jcvazquez@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import sys, logging
from datetime import date
from odoo import fields, models, api
from openerp.osv import osv
from odoo.tools.float_utils import float_compare, float_round
from openerp.exceptions import ValidationError


_logger = logging.getLogger(__name__)


class stock_picking(models.Model):
    _inherit = 'stock.picking'

    document_id = fields.Many2one(
        'stock.picking.documents',
        string='Documento',
    )
    number = fields.Char(
        string='Numero',
        size=15,
    )
    reason_id = fields.Many2one(
        'stock.picking.reasons',
        string='Motivo',
    )
    description = fields.Text(
        string='Descripción',
    )


    @api.multi
    def action_draft(self):
        self.state = 'draft'


    @api.multi
    def confirm_availability(self):
        _logger.warning("Hola")
        self.action_assign()

    
    @api.multi
    def on_hold_gi(self):
        self.show_check_availability = True
        self.state = "confirmed"

    @api.multi
    def validate_gi(self):
        """
        Este método sirve para crear entradas, cuando las cantidades coincidan y se manda a llamar el método de procesar por defecto de odoo.
        Debe de hacerse pruebas exhaustivas ya que esta funcionalidad es utilizada en muchas parte del ERP
        """
        validate_ok =  True
        for move_line in self.move_lines:
            reserved_availability = move_line.reserved_availability
            spl = str(move_line.reserved_availability).split(".")
            if len(spl[1]) > 3:
                reserved_availability = float("{0:.3f}".format(reserved_availability))
            quantity_done = move_line.quantity_done
            spl = str(quantity_done).split(".")
            if len(spl[1]) > 3:
                quantity_done = float("{0:.3f}".format(quantity_done))
            if quantity_done != reserved_availability:
                validate_ok = False

        if validate_ok:

            purchases_order = self.env['purchase.order'].sudo().search([('name', '=', self.origin)], limit=1)

            if purchases_order:
                for move_line in self.move_lines:

                    if move_line.product_id.type == 'consu' or move_line.product_id.type == 'product':


                        for line_id in move_line.move_line_ids:

                            if line_id.qty_done > 0.0:
                                reception_id = self.env['purchase.reception'].create({'product_id': line_id.product_id.id, 'order_id': purchases_order.id, 'qty': line_id.qty_done, 'get_qty': line_id.qty_done, 'state': 'received','date_request': fields.Date.today(), 'move_line': line_id.id, 'company_id' : self.company_id.id, 'picking_id':self.id, 'purchase_line_id': move_line.purchase_line_id.id})

                                folio_sequence = self.env['ir.sequence'].sudo().search([('name', '=', 'reception'),('company_id','=', self.company_id.id)], limit=1)

                                if not folio_sequence:
                                    raise ValidationError('No está configurada una secuencia "Orden de compra" para la compañía.')
                                reception_id.name = folio_sequence._next()


                            line_id.lot_name = reception_id.name


            if self.location_dest_id.get_lot:
                for move_line_id in self.move_line_ids:
                    if move_line_id.lot_id:
                        if not move_line_id.lot_id.ref:
                            raise ValidationError('No está configurado correctamente el "Lote del proveedor". Configuro en el lote titulado ' + move_line_id.lot_id.name)


            if self.location_dest_id.check_tags:

                for move_line_id in self.move_line_ids:

                    if not move_line_id.lot_id.product_id:
                        raise ValidationError('No está configurado correctamente el "Producto".')

                    if not move_line_id.lot_id.product_id.default_code:
                        raise ValidationError('No está configurado correctamente la "Referencia interna del producto".')

                    if not move_line_id.lot_id.product_id.type_expiration:
                        raise ValidationError('No está configurado correctamente el "Tipo de vigencia en el producto".')

                    if not move_line_id.lot_id.life_date:
                        raise ValidationError('No está configurado correctamente la "Fecha de vigencia en el lote".')

                    if not move_line_id.lot_id.num_container:
                        raise ValidationError('No está configurado correctamente la "Número de contenedores en el lote".')


                    self.env['control.tags.printer'].create({
                        'name': move_line_id.lot_id.id,
                        'name_char': move_line_id.lot_id.name,
                        'company_id': self.company_id.name,
                        'lot_sup': move_line_id.lot_id.ref,
                        'product_id': move_line_id.lot_id.product_id.name,
                        'default_code': move_line_id.lot_id.product_id.default_code,
                        'type_date': move_line_id.lot_id.product_id.type_expiration,
                        'life_date': move_line_id.lot_id.life_date,
                        'num_container': move_line_id.lot_id.num_container,
                        'printer': 0,
                    })


                return self.button_validate()

            else:
                for move_line in self.move_lines:
                    if move_line.quantity_done != move_line.reserved_availability:
                       move_line.lot_name = "Borrador"

                if not self.origin:

                    for move_line in self.move_lines:
                        if move_line.quantity_done > move_line.reserved_availability:
                            raise ValidationError("La cantidad a procesar es  mayor a la que se tiene en stock.")



                return self.button_validate()
        else:

            for move_line in self.move_lines:
                for move_line_id in move_line.move_line_ids:
                   move_line_id.lot_name = "Borrador"

            return self.button_validate()