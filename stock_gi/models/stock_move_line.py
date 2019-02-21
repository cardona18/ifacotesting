# -*- coding: utf-8 -*-
# © <2016> <Juan Carlos Vazquez Beas (jcvazquez@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from dateutil import tz
from datetime import datetime
from odoo import fields, models, api
from odoo.exceptions import UserError
from openerp.exceptions import ValidationError
from odoo.tools.float_utils import float_round, float_compare, float_is_zero

_logger = logging.getLogger(__name__)

class stock_move_line(models.Model):
    _inherit = 'stock.move.line'
   

    # @api.onchange('qty_done')
    # def onchange_qty_done(self):
    #     if self.qty_done > self.product_uom_qty:
    #         raise ValidationError("La cantidad a procesar es  mayor a la que se tiene en stock.")

    @api.multi
    def write(self, vals):
        try:
            if self.picking_id:
                if not self.picking_id.origin:
                    if vals['qty_done']:
                        if vals['qty_done'] > self.product_uom_qty:
                            vals['qty_done'] = 0
                            raise ValidationError("La cantidad a procesar es  mayor a la que se tiene en stock.___")

        except Exception as e:
            pass

        return super(stock_move_line, self).write(vals)

    def unlink(self):
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        for ml in self:
            if ml.state in ('done', 'cancel'):
                raise UserError(_('You can not delete product moves if the picking is done. You can only correct the done quantities.'))
            # Unlinking a move line should unreserve.
            if ml.product_id.type == 'product' and not ml.location_id.should_bypass_reservation() and not float_is_zero(ml.product_qty, precision_digits=precision):
                try:
                    self.env['stock.quant']._update_reserved_quantity(ml.product_id, ml.location_id, -ml.product_qty, lot_id=ml.lot_id, package_id=ml.package_id, owner_id=ml.owner_id, strict=True)
                except UserError:
                    if ml.lot_id:
                        self.env['stock.quant']._update_reserved_quantity(ml.product_id, ml.location_id, -ml.product_qty, lot_id=False, package_id=ml.package_id, owner_id=ml.owner_id, strict=True)
                    else:
                        raise
        moves = self.mapped('move_id')
        return models.Model.unlink(self)

