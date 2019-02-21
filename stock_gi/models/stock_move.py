# -*- coding: utf-8 -*-
# © <2016> <Juan Carlos Vazquez Beas (jcvazquez@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from dateutil import tz
from dateutil import relativedelta
from datetime import datetime
from odoo import fields, models, api, _
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
from odoo.addons import decimal_precision as dp
from odoo.tools.float_utils import float_compare, float_round, float_is_zero
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT,DEFAULT_SERVER_DATETIME_FORMAT
_logger = logging.getLogger(__name__)

class stock_move_line(models.Model):
    _inherit = 'stock.move'
   
    # @api.onchange('move_line_ids')
    # def onchange_move_line_ids(self):
    #     for move_line_id in self.move_line_ids:
    #         if move_line_id.qty_done > move_line_id.product_uom_qty:
    #             if not move_line_id.picking_id.origin:
    #                     raise ValidationError("La cantidad a procesar es  mayor a la que se tiene en stock.")

    def _get_qty_done_dec(self):
        for rec in self:
            amount = 0
            for move_line in rec.move_line_ids:
                amount += move_line.qty_done
            rec.qty_done_dec = amount

    qty_done_dec = fields.Float(string='Cantidad', digits=dp.get_precision('Product Unit of Measure'), compute=_get_qty_done_dec)

    def _create_extra_move(self):
        """ If the quantity done on a move exceeds its quantity todo, this method will create an
        extra move attached to a (potentially split) move line. If the previous condition is not
        met, it'll return an empty recordset.

        The rationale for the creation of an extra move is the application of a potential push
        rule that will handle the extra quantities.
        """
        extra_move = self.env['stock.move']
        rounding = self.product_uom.rounding
        # moves created after the picking is assigned do not have `product_uom_qty`, but we shouldn't create extra moves for them
        if float_compare(self.quantity_done, self.product_uom_qty, precision_rounding=rounding) > 0:
            # create the extra moves
            extra_move_quantity = float_round(
                self.quantity_done - self.product_uom_qty,
                precision_rounding=self.product_uom.rounding,
                rounding_method='UP')
            # ***********bloque de lineas que agregue Freddy***************
            res_extra_move = self.quantity_done - self.product_uom_qty
            if res_extra_move != extra_move_quantity:
                extra_move_quantity = res_extra_move
            # ****************************
            extra_move_vals = self._prepare_extra_move_vals(extra_move_quantity)
            extra_move = self.copy(default=extra_move_vals)._action_confirm()

            # link it to some move lines. We don't need to do it for move since they should be merged.
            if self.exists() and not self.picking_id:
                for move_line in self.move_line_ids.filtered(lambda ml: ml.qty_done):
                    if float_compare(move_line.qty_done, extra_move_quantity, precision_rounding=rounding) <= 0:
                        # move this move line to our extra move
                        move_line.move_id = extra_move.id
                        extra_move_quantity -= move_line.qty_done
                    else:
                        # split this move line and assign the new part to our extra move
                        quantity_split = float_round(
                            move_line.qty_done - extra_move_quantity,
                            precision_rounding=self.product_uom.rounding,
                            rounding_method='UP')
                        move_line.qty_done = quantity_split
                        move_line.copy(
                            default={'move_id': extra_move.id, 'qty_done': extra_move_quantity, 'product_uom_qty': 0})
                        extra_move_quantity -= extra_move_quantity
                    if extra_move_quantity == 0.0:
                        break
        return extra_move

    def _action_done(self):
        self.filtered(lambda move: move.state == 'draft')._action_confirm()  # MRP allows scrapping draft moves

        moves = self.filtered(lambda x: x.state not in ('done', 'cancel'))
        moves_todo = self.env['stock.move']
        # Create extra moves where necessary
        for move in moves:
            # Here, the `quantity_done` was already rounded to the product UOM by the `do_produce` wizard. However,
            # it is possible that the user changed the value before posting the inventory by a value that should be
            # rounded according to the move's UOM. In this specific case, we chose to round up the value, because it
            # is what is expected by the user (if i consumed/produced a little more, the whole UOM unit should be
            # consumed/produced and the moves are split correctly).
            # FIXME: move rounding to move line
            # rounding = move.product_uom.rounding
            # move.quantity_done = float_round(move.quantity_done, precision_rounding=rounding, rounding_method ='UP')
            if move.quantity_done <= 0:
                if float_compare(move.product_uom_qty, 0.0, precision_rounding=move.product_uom.rounding) == 0:
                    move._action_cancel()
                continue
            moves_todo |= move
            moves_todo |= move._create_extra_move()
        # Split moves where necessary and move quants
        for move in moves_todo:
            rounding = move.product_uom.rounding
            if float_compare(move.quantity_done, move.product_uom_qty, precision_rounding=rounding) < 0:
                # Need to do some kind of conversion here
                qty_split = move.product_uom._compute_quantity(move.product_uom_qty - move.quantity_done, move.product_id.uom_id)
                # ***********bloque de lineas que agregue Freddy***************
                new_qty = move.product_uom_qty - move.quantity_done
                if new_qty != qty_split:
                    qty_split = new_qty
                # ****************************
                new_move = move._split(qty_split)
                for move_line in move.move_line_ids:
                    if move_line.product_qty and move_line.qty_done:
                        # FIXME: there will be an issue if the move was partially available
                        # By decreasing `product_qty`, we free the reservation.
                        # FIXME: if qty_done > product_qty, this could raise if nothing is in stock
                        try:
                            move_line.write({'product_uom_qty': move_line.qty_done})
                        except UserError:
                            pass

                # If you were already putting stock.move.lots on the next one in the work order, transfer those to the new move
                move.move_line_ids.filtered(lambda x: x.qty_done == 0.0).write({'move_id': new_move})
            move.move_line_ids._action_done()
        picking = self and self[0].picking_id or False
        moves_todo.write({'state': 'done', 'date': fields.Datetime.now()})
        moves_todo.mapped('move_dest_ids')._action_assign()

        # We don't want to create back order for scrap moves
        if all(move_todo.scrapped for move_todo in moves_todo):
            return moves_todo

        #apagador = False
        if picking:
            moves_to_backorder = picking.move_lines.filtered(lambda x: x.state not in ('done', 'cancel'))
            if moves_to_backorder:
                backorder_picking = picking.copy({
                        'name': '/',
                        'move_lines': [],
                        'move_line_ids': [],
                        'backorder_id': picking.id
                    })
                picking.message_post(_('The backorder <a href=# data-oe-model=stock.picking data-oe-id=%d>%s</a> has been created.') % (backorder_picking.id, backorder_picking.name))
                moves_to_backorder.write({'picking_id': backorder_picking.id})
                moves_to_backorder.mapped('move_line_ids').write({'picking_id': backorder_picking.id})
            moves_to_backorder._action_assign()
        return moves_todo

    def write(self, vals):
        # FIXME: pim fix your crap
        receipt_moves_to_reassign = self.env['stock.move']
        if 'product_uom_qty' in vals:
            for move in self.filtered(lambda m: m.state not in ('done', 'draft') and m.picking_id):
                if vals['product_uom_qty'] != move.product_uom_qty:
                    self.env['stock.move.line']._log_message(move.picking_id, move, 'stock.track_move_template', vals)
            if self.env.context.get('do_not_unreserve') is None:
                move_to_unreserve = self.filtered(lambda m: m.state not in ['draft', 'done', 'cancel'] and m.reserved_availability > vals.get('product_uom_qty'))
                move_to_unreserve._do_unreserve()
                (self - move_to_unreserve).filtered(lambda m: m.state == 'assigned').write({'state': 'partially_available'})
                # When editing the initial demand, directly run again action assign on receipt moves.
                receipt_moves_to_reassign |= move_to_unreserve.filtered(lambda m: m.location_id.usage == 'supplier')
                receipt_moves_to_reassign |= (self - move_to_unreserve).filtered(lambda m: m.location_id.usage == 'supplier' and m.state in ('partially_available', 'assigned'))

        # TDE CLEANME: it is a gros bordel + tracking
        Picking = self.env['stock.picking']

        propagated_changes_dict = {}
        #propagation of expected date:
        propagated_date_field = False
        if vals.get('date_expected'):
            #propagate any manual change of the expected date
            propagated_date_field = 'date_expected'
        elif (vals.get('state', '') == 'done' and vals.get('date')):
            #propagate also any delta observed when setting the move as done
            propagated_date_field = 'date'

        if not self._context.get('do_not_propagate', False) and (propagated_date_field or propagated_changes_dict):
            #any propagation is (maybe) needed
            for move in self:
                if move.move_dest_ids and move.propagate:
                    if 'date_expected' in propagated_changes_dict:
                        propagated_changes_dict.pop('date_expected')
                    if propagated_date_field:
                        #CAMBIOS FREDDY
                        current_date = datetime.strptime(move.date_expected, DEFAULT_SERVER_DATETIME_FORMAT)
                        if len(vals[propagated_date_field]) > 10:
                            date_validate = datetime.strptime(vals.get(propagated_date_field), DEFAULT_SERVER_DATETIME_FORMAT)
                            if(date_validate.hour >= 0):
                                date_validate = date_validate.replace(hour=0, minute=0, second=0)
                                new_date = date_validate
                                vals[propagated_date_field] = str(new_date)
                            else:
                                new_date = datetime.strptime(vals.get(propagated_date_field), DEFAULT_SERVER_DATE_FORMAT)
                        else:
                            new_date = datetime.strptime(vals.get(propagated_date_field), DEFAULT_SERVER_DATE_FORMAT)
                        delta_days = (new_date - current_date).total_seconds() / 86400
                        if abs(delta_days) >= move.company_id.propagation_minimum_delta:
                            old_move_date = datetime.strptime(move.move_dest_ids[0].date_expected, DEFAULT_SERVER_DATETIME_FORMAT)
                            new_move_date = (old_move_date + relativedelta.relativedelta(days=delta_days or 0)).strftime(DEFAULT_SERVER_DATE_FORMAT)
                            propagated_changes_dict['date_expected'] = new_move_date
                    #For pushed moves as well as for pulled moves, propagate by recursive call of write().
                    #Note that, for pulled moves we intentionally don't propagate on the procurement.
                    if propagated_changes_dict:
                        move.move_dest_ids.filtered(lambda m: m.state not in ('done', 'cancel')).write(propagated_changes_dict)
        track_pickings = not self._context.get('mail_notrack') and any(field in vals for field in ['state', 'picking_id', 'partially_available'])
        if track_pickings:
            to_track_picking_ids = set([move.picking_id.id for move in self if move.picking_id])
            if vals.get('picking_id'):
                to_track_picking_ids.add(vals['picking_id'])
            to_track_picking_ids = list(to_track_picking_ids)
            pickings = Picking.browse(to_track_picking_ids)
            initial_values = dict((picking.id, {'state': picking.state}) for picking in pickings)
        res = models.Model.write(self, vals)
        if track_pickings:
            pickings.message_track(pickings.fields_get(['state']), initial_values)
        if receipt_moves_to_reassign:
            receipt_moves_to_reassign._action_assign()
        return res
