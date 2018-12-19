# -*- coding: utf-8 -*-
# © <2018> < ()>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging

from odoo import fields, models, api

_logger = logging.getLogger(__name__)


class account_invoice_refund_gi(models.Model):
    _inherit = 'account'

    comments = fields.Text(
        string='Comentarios',


    )
