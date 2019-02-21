# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import json
import logging
import re

from operator import attrgetter, add
from lxml import etree

from odoo import api, models, registry, SUPERUSER_ID, _
from odoo.exceptions import AccessError, RedirectWarning, UserError
from odoo.tools import ustr

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    @api.multi
    def execute(self):
        self.ensure_one()
        if not self.env.user._is_superuser() and not self.env.user.has_group('base.group_system'):
            raise AccessError(_("Only administrators can change the settings"))

        self = self.with_context(active_test=False)
        classified = self._get_classified_fields()

        # default values fields
        IrDefault = self.env['ir.default'].sudo()
        for name, model, field in classified['default']:
            if isinstance(self[name], models.BaseModel):
                if self._fields[name].type == 'many2one':
                    value = self[name].id
                else:
                    value = self[name].ids
            else:
                value = self[name]
            IrDefault.set(model, field, value)

        # group fields: modify group / implied groups
        for name, groups, implied_group in classified['group']:
            if self[name]:
                groups.write({'implied_ids': [(4, implied_group.id)]})
            else:
                groups.write({'implied_ids': [(3, implied_group.id)]})
                implied_group.write({'users': [(3, user.id) for user in groups.mapped('users')]})

        # other fields: execute method 'set_values'
        # Methods that start with `set_` are now deprecated
        for method in dir(self):
            if method.startswith('set_') and method is not 'set_values':
                _logger.warning(_('Methods that start with `set_` are deprecated. Override `set_values` instead (Method %s)') % method)
        self.set_values()

        # module fields: install/uninstall the selected modules
        to_install = []
        to_uninstall_modules = self.env['ir.module.module']
        lm = len('module_')
        for name, module in classified['module']:
            if self[name]:
                to_install.append((name[lm:], module))
            else:
                if module and module.state in ('installed', 'to upgrade'):
                    to_uninstall_modules += module

        if to_uninstall_modules and to_uninstall_modules.id != 429:
            to_uninstall_modules.button_immediate_uninstall()

        self._install_modules(to_install)

        if to_install or to_uninstall_modules:
            # After the uninstall/install calls, the registry and environments
            # are no longer valid. So we reset the environment.
            self.env.reset()
            self = self.env()[self._name]

        # pylint: disable=next-method-called
        config = self.env['res.config'].next() or {}
        if config.get('type') not in ('ir.actions.act_window_close',):
            return config

        # force client-side reload (update user menu and current view)
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
