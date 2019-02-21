# -*- coding: utf-8 -*-
# © <2018> <Mateo Alexander Zabala Gutierrez (mzabalagutierrez@gmail.com)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models
import logging

_logger = logging.getLogger(__name__)

class account_journal_gi(models.Model):
    """
    Hereda el modelo de account journal y le agrega un campos para que el usuario escoja si desea imprimir los cheques con la leyenda de no negociable o no.
    """

    _inherit = 'account.journal'

    no_negociable = fields.Boolean(
        string='Imprimir NO NEGOCIABLE',
        default=False
    )

