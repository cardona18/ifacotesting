# -*- coding: utf-8 -*-
# © <2018> <Omar Torres (otorresgi18@gmail.com)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api

import base64
from io import StringIO
import csv
import logging

_logger = logging.getLogger(__name__)

class sale_bidding_codes_wizard(models.TransientModel):
    _name = 'sale.bidding.codes.wizard'
    _description = 'SALE BIDDING CODES WIZARD'

    bidding_id = fields.Many2one(
        string='Licitación',
        comodel_name='sale.bidding'
    )
    csv_file = fields.Binary(
        string='Productos ganados',
        help="""Archivo en formato CSV con claves de producto ganadas en la licitación en el formato:
        Clave cliente, Clave producto, Cantidad, Precio, Impuesto
        """
    )
    csv_filename = fields.Char(
        string='Claves (Archivo)'
    )
    log_result = fields.Text(
        string='Resultado'
    )
    stage = fields.Selection(
        string='Face',
        default='I',
        selection=[
            ('I', 'Inicio'),
            ('R', 'Resultado')
        ]
    )

    @api.multi
    def process_product_codes(self):

        file_content = base64.b64decode(self.csv_file)
        file_lines = StringIO(file_content.decode('UTF-8'))
        csv_lines = list(csv.reader(file_lines, delimiter=','))
        grouped_lines = {}
        line_count = 0

        for csv_line in csv_lines:

            line_count += 1

            if line_count == 1:
                continue

            ccode = csv_line.pop(0)

            if not ccode:
                continue

            if ccode not in grouped_lines.keys():
                grouped_lines[ccode] = []

            grouped_lines[ccode].append(csv_line)


        for ccode in grouped_lines:

            customer = self.env['res.partner'].search([
                ('customer', '=', True),
                ('ref', '=', ccode)
            ], limit=1)

            sale_order = self.env['sale.order'].create({
                'partner_id': customer.id,
                'bidding_id': self.bidding_id.id
            })

            for cline in grouped_lines[ccode]:

                product = self.env['product.product'].search([
                    ('sale_ok', '=', True),
                    ('default_code', '=', cline[0])
                ], limit=1)

                if not product.id:
                    continue

                line_values = {
                    'order_id': sale_order.id,
                    'name': product.name,
                    'product_id': product.id,
                    'product_uom_qty': float(cline[1]),
                    'price_unit': float(cline[2])
                }

                tax_id = self.env['account.tax'].search([
                    ('type_tax_use', '=', 'sale'),
                    ('amount', '=', cline[3])
                ], limit=1).id

                if tax_id:
                    line_values['tax_id'] = [(6,0,[tax_id])]

                self.env['sale.order.line'].create(line_values)