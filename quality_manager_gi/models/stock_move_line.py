# -*- coding: utf-8 -*-
# © <2016> <Juan Carlos Vazquez Beas (jcvazquez@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from dateutil import tz
from datetime import datetime
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_round, float_compare, float_is_zero

_logger = logging.getLogger(__name__)

class stock_move_line(models.Model):
    _inherit = 'stock.move.line'


    life_date = fields.Datetime(
        related='lot_id.life_date',
        string='Fecha de vigencia',
        help='La "Fecha de vigencia" debe de ser mayor a la actual'
    )
    lot_refer = fields.Char(
        related="lot_id.ref",
        string='Lote proveedor',
        store=True,
    )
    date_analysis = fields.Date(
        related='lot_id.date_analysis',
        string='Fecha de análisis'
    )
    doc_number  = fields.Integer(
        related='lot_id.doc_number',
        string='Número de documento',
        size=10, 
    )
    num_container  = fields.Integer(
        related='lot_id.num_container',
        string='Número de contenedores',
        size=4,         
    )    
    employee_id = fields.Many2one(
        related='lot_id.employee_id',
        string='Nombre del analista',
        domain=[('is_analysis','=',True), ]
    )
    valuation = fields.Float(
        related='lot_id.valuation',
        string='Valoración',
    )
    unit_valuation = fields.Selection(
        related='lot_id.unit_valuation',
        string='Unidad de valoración',
        size=5,
        selection=[
            ('ave', '%'),
            ('uimg', 'UI/mg'),
            ('mcg', 'mcg/mg'),
            ('uiml', 'UI/ml'),
        ]
    )
    approved_lot = fields.Boolean(
        string='Aprobar control',
    )
    supplier_lot = fields.Char(string='Lote proveedor', invisible=True)

    def _get_value_visible(self):
        for rec in self:
            if rec.picking_id.picking_type_code != 'incoming':
                rec.visible_field = True

    visible_field = fields.Boolean(default=False, compute=_get_value_visible)



    def get_data_time(self):
        current_date = self._utc_to_tz(datetime.now(), "America/Mexico_City")
        current_date = str(current_date.isoformat())[:19]

        return current_date

    def _utc_to_tz(self, _date, _time_zone):
        # CONVER TO UTC
        _date = _date.replace(tzinfo = tz.gettz('UTC'))
        # LOAD TIMEZONE
        to_zone  = tz.gettz(_time_zone)
        return _date.astimezone(to_zone)


    @api.onchange('life_date')
    def onchange_life_date(self):
        if self.get_data_time() > self.life_date:
            self.life_date = None
            return {
                'life_date' : {'life_date': None},
                'warning': {'title': "Warning", 'message': "Fecha de vigencia debe ser mayor a la fecha actual."},
            }


    def _action_done(self):
        """ This method is called during a move's `action_done`. It'll actually move a quant from
        the source location to the destination location, and unreserve if needed in the source
        location.

        This method is intended to be called on all the move lines of a move. This method is not
        intended to be called when editing a `done` move (that's what the override of `write` here
        is done.
        """

        # First, we loop over all the move lines to do a preliminary check: `qty_done` should not
        # be negative and, according to the presence of a picking type or a linked inventory
        # adjustment, enforce some rules on the `lot_id` field. If `qty_done` is null, we unlink
        # the line. It is mandatory in order to free the reservation and correctly apply
        # `action_done` on the next move lines.
        ml_to_delete = self.env['stock.move.line']
        for ml in self:
            qty_done_float_compared = float_compare(ml.qty_done, 0, precision_rounding=ml.product_uom_id.rounding)
            if qty_done_float_compared > 0:
                if ml.product_id.tracking != 'none':
                    picking_type_id = ml.move_id.picking_type_id
                    if picking_type_id:
                        if picking_type_id.use_create_lots:
                            # If a picking type is linked, we may have to create a production lot on
                            # the fly before assigning it to the move line if the user checked both
                            # `use_create_lots` and `use_existing_lots`.
                            if ml.lot_name and not ml.lot_id:
                                orden_compra = self.env['purchase.order'].search([('name','=',ml.picking_id.origin)])
                                if orden_compra:
                                    lot = self.env['stock.production.lot'].create(
                                        {'name': ml.lot_name, 'product_id': ml.product_id.id, 'ref': ml.supplier_lot,
                                         'partner_id':orden_compra.partner_id.id,'company_id':orden_compra.company_id.id}
                                    )
                                else:
                                    lot = self.env['stock.production.lot'].create(
                                        {'name': ml.lot_name, 'product_id': ml.product_id.id, 'ref' : ml.supplier_lot}
                                    )
                                ml.write({'lot_id': lot.id})
                        elif not picking_type_id.use_create_lots and not picking_type_id.use_existing_lots:
                            # If the user disabled both `use_create_lots` and `use_existing_lots`
                            # checkboxes on the picking type, he's allowed to enter tracked
                            # products without a `lot_id`.
                            continue
                    elif ml.move_id.inventory_id:
                        # If an inventory adjustment is linked, the user is allowed to enter
                        # tracked products without a `lot_id`.
                        continue

                    if not ml.lot_id:
                        raise UserError(_('You need to supply a lot/serial number for %s.') % ml.product_id.name)
            elif qty_done_float_compared < 0:
                raise UserError(_('No negative quantities allowed'))
            else:
                ml_to_delete |= ml
        ml_to_delete.unlink()

        # Now, we can actually move the quant.
        for ml in self - ml_to_delete:
            if ml.product_id.type == 'product':
                Quant = self.env['stock.quant']
                rounding = ml.product_uom_id.rounding

                # if this move line is force assigned, unreserve elsewhere if needed
                if not ml.location_id.should_bypass_reservation() and float_compare(ml.qty_done, ml.product_qty, precision_rounding=rounding) > 0:
                    extra_qty = ml.qty_done - ml.product_qty
                    ml._free_reservation(ml.product_id, ml.location_id, extra_qty, lot_id=ml.lot_id, package_id=ml.package_id, owner_id=ml.owner_id)
                # unreserve what's been reserved
                if not ml.location_id.should_bypass_reservation() and ml.product_id.type == 'product' and ml.product_qty:
                    try:
                        Quant._update_reserved_quantity(ml.product_id, ml.location_id, -ml.product_qty, lot_id=ml.lot_id, package_id=ml.package_id, owner_id=ml.owner_id, strict=True)
                    except UserError:
                        Quant._update_reserved_quantity(ml.product_id, ml.location_id, -ml.product_qty, lot_id=False, package_id=ml.package_id, owner_id=ml.owner_id, strict=True)

                # move what's been actually done
                quantity = ml.product_uom_id._compute_quantity(ml.qty_done, ml.move_id.product_id.uom_id, rounding_method='HALF-UP')
                available_qty, in_date = Quant._update_available_quantity(ml.product_id, ml.location_id, -quantity, lot_id=ml.lot_id, package_id=ml.package_id, owner_id=ml.owner_id)
                if available_qty < 0 and ml.lot_id:
                    # see if we can compensate the negative quants with some untracked quants
                    untracked_qty = Quant._get_available_quantity(ml.product_id, ml.location_id, lot_id=False, package_id=ml.package_id, owner_id=ml.owner_id, strict=True)
                    if untracked_qty:
                        taken_from_untracked_qty = min(untracked_qty, abs(quantity))
                        Quant._update_available_quantity(ml.product_id, ml.location_id, -taken_from_untracked_qty, lot_id=False, package_id=ml.package_id, owner_id=ml.owner_id)
                        Quant._update_available_quantity(ml.product_id, ml.location_id, taken_from_untracked_qty, lot_id=ml.lot_id, package_id=ml.package_id, owner_id=ml.owner_id)
                Quant._update_available_quantity(ml.product_id, ml.location_dest_id, quantity, lot_id=ml.lot_id, package_id=ml.result_package_id, owner_id=ml.owner_id, in_date=in_date)
        # Reset the reserved quantity as we just moved it to the destination location.
        (self - ml_to_delete).with_context(bypass_reservation_update=True).write({'product_uom_qty': 0.00})
