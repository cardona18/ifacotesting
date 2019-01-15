# -*- coding: utf-8 -*-
# © <2018> < ()>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
from odoo import fields, models, api

import itertools
import psycopg2

from odoo.addons import decimal_precision as dp

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, RedirectWarning, except_orm
from odoo.tools import pycompat

_logger = logging.getLogger(__name__)


class product_template_gi(models.Model):
    _inherit = 'product.template'

    def get_group(self):
        for self_id in self:
            self_id.perm_categ = self.env.user.has_group(('purchases_gi.manager_purchases','purchase.group_purchase_manager','account_gi.accountant','stock.group_stock_manager'))

    perm_categ = fields.Boolean(
        string='Con permisos de programar pagos',
        compute=get_group,
    )


