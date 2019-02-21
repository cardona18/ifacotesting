# -*- coding: utf-8 -*-
# © <2017> <Juan Carlos Vazquez Beas (jcvazquez@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import sys, logging
from odoo import fields, models, api
from openerp.exceptions import ValidationError


_logger = logging.getLogger(__name__)

class product_gi(models.Model):
    """Documentation for a class product_gi inherit = 'product.template'.
    Esta clase es heredada para agregar funcionalidades especificas para la lógica de negocio.
    """
    _inherit = 'product.template'

    barcode = fields.Char(
        string='Código de barras',
        size=13, 
    )


    def calc_check_digit(self, first12digits):
        """Documentation for a function, 'calc_check_digit'.
            Esta función ayuda calcula en número verificador del EAN 13.
        """
        charList = [char for char in first12digits]
        ean13 = [1,3]
        total = 0
        for order, char in enumerate(charList):
            total += int(char) * ean13[order % 2]

        checkDigit = 10 - total % 10
        if (checkDigit == 10):
            return 0
        return checkDigit


    @api.multi
    def calculate_barcode_ean_13(self):
        """Documentation for a function, 'calc_check_digit'.
            Esta función es llamada desde el botón 'generar código de barras' calcula el dígito siguiente del producto y llama la función de verificador.
        """
        barcode_calculate = "750"
        if self.company_id.code_ean and len(self.company_id.code_ean) == 5:
            barcode_calculate = barcode_calculate+self.company_id.code_ean
            prod_ids = self.env['product.product'].search([('company_id','=', self.company_id.id),('barcode', '!=', None),'|',('active','=',True),('active','=',False)])
            product_codes = []

            if len(prod_ids) == 0:
                prod_num = str('%04d' % int(1))

                barcode_calculate = str(barcode_calculate)+str(prod_num)
                barcode_calculate = str(barcode_calculate)+str(self.calc_check_digit(barcode_calculate))

            else:

                for product in prod_ids:
                    key_prod = int(product.barcode[8:12])
                    product_codes.append(key_prod)

                id_arra = len(product_codes) -1
                product_orden = sorted(product_codes)
                barcode_calculate = barcode_calculate+'%04d' % int(product_orden[id_arra]+ 1)
                barcode_calculate = str(barcode_calculate)+str(self.calc_check_digit(barcode_calculate))


        else:
            raise ValidationError('No está configurado correctamente la "Clave para código de barras" favor de configurarlo en la empresa.')


        self.barcode =  barcode_calculate

