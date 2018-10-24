# -*- coding: utf-8 -*-
# © <2017> <Juan Carlos Vazquez Beas (jcvazquez@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import sys, logging
from odoo import fields, models, api
from openerp.exceptions import ValidationError


_logger = logging.getLogger(__name__)

class product_packaging(models.Model):
    """Documentation for a class product_packaging inherit = 'product.packaging'.
    Esta clase es heredada para agregar funcionalidades especificas para la lógica de negocio.
    """
    _inherit = 'product.packaging'

    active = fields.Boolean(
        string='Archivado',
        default=True
    )

    barcode = fields.Char(
        string='Código de barras',
        size=14, 
    )

    def calc_check_digit(self, first13digits):
        """Documentation for a function, 'calc_check_digit'.
            Esta función ayuda calcula en número verificador del DUM 14.
        """
        charList = [char for char in first13digits]
        ean13 = [3,1]
        total = 0
        for order, char in enumerate(charList):
            total += int(char) * ean13[order % 2]

        checkDigit = 10 - total % 10
        if (checkDigit == 10):
            return 0

        return checkDigit


    @api.multi
    def calculate_barcode_dum(self):
        """Documentation for a function, 'calculate_barcode_dums'.
            Esta función es llamada desde el botón 'generar código de barras' calcula el dígito siguiente del producto y llama la función de verificador.
        """
        barcode_calculate = None

        if self.product_id.barcode:

            barcode_12 = self.product_id.barcode[0:12]

            prod_ids = self.env['product.packaging'].search([('product_id','=', self.product_id.id),('barcode', '!=', ''),'|',('active','=',True),('active','=',False)])
            product_codes = []


            if len(prod_ids) == 0:

                barcode13 = '1' + barcode_12
                barcode_calculate = str(barcode13)+str(self.calc_check_digit(barcode13))



            else:
                for product in prod_ids:


                    if product.barcode:
                        key_prod = int(product.barcode[0:1])
                        product_codes.append(key_prod)

                              
                if not product_codes:                   
                    barcode13 = '1' + barcode_12
                    if int(barcode13[0:1]) > 9:
                        raise ValidationError('No se ha pueden crear más de 10 paquetes.')
                    barcode_calculate = str(barcode13)+str(self.calc_check_digit(barcode13))

                else:
                    id_arra = len(product_codes) -1
                    product_orden = sorted(product_codes)
                    _logger.warning(barcode_calculate)
                    _logger.warning(int(product_orden[id_arra]+ 1))
                    if not barcode_calculate:
                        if int(product_orden[id_arra]+ 1) > 9:
                            if len(product_codes) >= 9:
                                raise ValidationError('No se ha pueden crear más de 10 paquetes.')
                            else:

                                get_num = 0
                                cont_num = 0
                                while get_num == 0:                                   
                                    if not product_codes[cont_num] + 1 in product_codes:
                                        get_num = product_codes[cont_num] + 1
                                            
                                    cont_num += 1

                                barcode_calculate =  str(get_num) + str(barcode_12)
                                barcode_calculate = str(barcode_calculate)+str(self.calc_check_digit(barcode_calculate))

                        else:
                            barcode_calculate =  str(int(product_orden[id_arra]+ 1)) + str(barcode_12)
                            barcode_calculate = str(barcode_calculate)+str(self.calc_check_digit(barcode_calculate))


        else:
            raise ValidationError('No se ha generado el código EAN.')

        self.barcode =  barcode_calculate

