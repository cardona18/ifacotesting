# -*- coding: utf-8 -*-
# © <2016> <Juan Carlos Vazquez Beas (jcvazquez@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
from dateutil import tz
from datetime import datetime
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
from odoo import fields, models, api

_logger = logging.getLogger(__name__)


from odoo import fields, models, api

class quality_check(models.Model):
    _inherit = 'quality.check'

    move_line_ids   = fields.One2many(
        related='picking_id.move_line_ids',
        string='operaciones',
    )

    point_test_type_id = fields.Many2one(
        related='point_id.test_type_id',
        string='Tipo de control',
        store=True,
    )


    @api.multi
    def do_pass_gi(self):
        self.do_pass()

    @api.multi
    def do_fail_gi(self):
        self.do_fail()

    @api.multi
    def create_quality_check(self):

        quality_check_ids = self.env['quality.check'].search([('picking_id', '=', self.picking_id.id)])

        control_p = len(self.move_line_ids) - len(quality_check_ids)

        _logger.warning("Repeticiones")
        _logger.warning(quality_check_ids)
        _logger.warning(control_p)

        while len(self.env['quality.check'].search([('picking_id', '=', self.picking_id.id)])) < len(self.move_line_ids):
            quality_dupli_id = self.env['quality.check'].search([('picking_id', '=', self.picking_id.id)], limit=1)
            quality_dupli_id.copy()


        for move_line_id in self.move_line_ids:

            if move_line_id.life_date == False:
                raise ValidationError('Se debe de ingresar los "Fecha de vigencia, Nombre del analista, etc" por línea de producto')
            if datetime.strptime(move_line_id.life_date, "%Y-%m-%d %H:%M:%S") <= datetime.now():
                raise ValidationError('La fecha debe ser mayor a la actual')

            # if not move_line_id.valuation == 0.0:
            if move_line_id.valuation >=  self.point_id.tolerance_min and move_line_id.valuation <= self.point_id.tolerance_max:

                quality_check_id = self.env['quality.check'].search([('lot_id', '=', move_line_id.lot_id.id),('picking_id', '=', move_line_id.picking_id.id)], limit=1)

                if not quality_check_id:
                    quality_check_id = self.env['quality.check'].search([('picking_id', '=', move_line_id.picking_id.id),('lot_id', '=', None)], limit=1)
                    quality_check_id.lot_id = move_line_id.lot_id
                    quality_check_id.do_pass()


                _logger.warning("Si entra en la valoración")
            else:

                quality_check_id = self.env['quality.check'].search([('lot_id', '=', move_line_id.lot_id.id),('picking_id', '=', move_line_id.picking_id.id)], limit=1)

                if not quality_check_id:
                    quality_check_id = self.env['quality.check'].search([('picking_id', '=', move_line_id.picking_id.id),('lot_id', '=', None)], limit=1)
                    quality_check_id.lot_id = move_line_id.lot_id
                    quality_check_id.do_fail()


                _logger.warning("No entra en la valoración")

        else:
            quality_check_id = self.env['quality.check'].search([('lot_id', '=', move_line_id.lot_id.id),('picking_id', '=', move_line_id.picking_id.id)], limit=1)

            if not quality_check_id:
                quality_check_id = self.env['quality.check'].search([('picking_id', '=', move_line_id.picking_id.id),('lot_id', '=', None)], limit=1)
                if quality_check_id:
                    quality_check_id.lot_id = move_line_id.lot_id


                # if self.point_id.tolerance_min == 0.0 and self.point_id.tolerance_max == 0.0:


                #     quality_check_id = self.env['quality.check'].search([('picking_id', '=', move_line_id.picking_id.id)], limit=1)
                    

                #     quality_check_id.lot_id = move_line_id.lot_id
                #     quality_check_id.do_pass()


                #     _logger.warning("Si entra en la valoración")

    @api.multi
    def generate_quality_checks(self):

        while len(self.env['quality.check'].search([('picking_id', '=', self.picking_id.id)])) < len(self.move_line_ids):
            quality_dupli_id = self.env['quality.check'].search([('picking_id', '=', self.picking_id.id)], limit=1)
            quality_dupli_id.copy()


        """Verifica que cuadren los controles con los movimientos"""
        if len(self.env['quality.check'].search([('picking_id', '=', self.picking_id.id)])) > len(self.move_line_ids):
            for move_line_id in self.move_line_ids:
                cont_product = 0 
                for move_con_id in self.move_line_ids:
                    if move_con_id.product_id.id == move_line_id.product_id.id:
                        cont_product = cont_product + 1  


                    quality_to_unlink_id = self.env['quality.check'].search([('picking_id', '=', self.picking_id.id), ('product_id', '=', move_line_id.product_id.id)])
                    
                    if cont_product:
                        if len(quality_to_unlink_id) > cont_product:
                            unlink_id = None
                            for quality_unlink_id in quality_to_unlink_id:
                                quality_verific_unlink_id = self.env['quality.check'].search([('picking_id', '=', self.picking_id.id), ('product_id', '=', move_line_id.product_id.id)])
                                if len(quality_verific_unlink_id) > cont_product:
                                    unlink_id = quality_unlink_id

                            if unlink_id:
                                unlink_id.unlink()





        #Utilizar lotes de los movimientos
        for move_line_id in self.move_line_ids:

            quality_check_id = self.env['quality.check'].search([('picking_id', '=', move_line_id.picking_id.id)])


            for quality_id in quality_check_id:
                if quality_id.product_id.id == move_line_id.product_id.id:

                    if not quality_id.lot_id:
                        quality_id.lot_id = move_line_id.lot_id.id

                    if move_line_id.approved_lot:
                        quality_id.do_pass()

                    else:
                        quality_id.do_fail()