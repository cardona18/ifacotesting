# -*- coding: utf-8 -*-
# © <2018> <Mateo Alexander Zabala Gutierrez (mzabalagutierrez@gmail.com)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models
from odoo.exceptions import ValidationError
from .num2words import Numero_a_Texto
import logging
try:
    from num2words import num2words
except ImportError:
    logging.getLogger(__name__).warning("The num2words python library is not installed, l10n_mx_edi features won't be fully available.")
    num2words = None

_logger = logging.getLogger(__name__)


class account_payment_gi(models.Model):
    _inherit = 'account.payment'

    def amount_to_text(self, currency_id):
        """
        Convierte cantidades numéricas a palabras.
        """
        self.ensure_one()

        if not self.currency_id:
            raise ValidationError('Se debe configurar la moneda.')

        return Numero_a_Texto(self.amount)

