# -*- coding: utf-8 -*-
# © <2016> <Omar Torres Silva (otorres@grupoifaco.com.mx) >
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from openerp import fields, models
from odoo.exceptions import UserError
from openerp.tools.translate import _
from openerp.tools.safe_eval import safe_eval as eval

_logger = logging.getLogger(__name__)

class hr_paysheet_rule(models.Model):
    _name = 'hr.paysheet.rule'
    _description = 'Paysheet rule'

    _sql_constraints = [
        ('unique_paysheet_rule', 'unique(code, active)', 'Ya se registró una regla con el mismo código')
    ]

    def _default_priority(self):

        last = self.search([], limit=1, order='priority DESC')
        ret  = 10

        if(last.id):
            ret = last.priority + 10

        return ret

    _CODE_HELP = """Variables disponibles
categories: Categorias de nómina,
contract: Contrato del empleado,
employee: Empleado,
inputs: Entradas de nómina referenciadas por el prefijo I seguido del código de concepto en 3 cifras ej: inputs.I034,
logger: Logs del sistema,
payments: Movimientos extra del empleado,
paysheet: Nómina del empleado,
rules: Valores de las reglas calculadas,
tables: Referencia a tablas de nómina,
tools: Funcionalidades personalizadas"""

    name = fields.Char(
        string='Name',
        required=True,
        size=80
    )
    vtype = fields.Selection(
        string='Aplicación',
        default='L',
        required=True,
        size=1,
        selection=[
            ('G', 'Global'),
            ('L', 'Local')
        ]
    )
    replace_method = fields.Selection(
        string='Metodo de reemplazo',
        required=True,
        size=3,
        default='ADD',
        selection=[
            ('ADD', 'Sumar'),
            ('REP', 'Remplazar')
        ]
    )
    code = fields.Char(
        string='Clave',
        required=True,
        size=50,
        help='Iniciar valor con letra y omitir espacios'
    )
    concept_id = fields.Many2one(
        string='Concepto',
        comodel_name='hr.paysheet.concept'
    )
    category_ids = fields.Many2many(
        string='Categorias',
        comodel_name='hr.paysheet.category'
    )
    priority = fields.Integer(
        string='Prioridad',
        default=_default_priority
    )
    ctype = fields.Selection(
        string='Tipo',
        required=True,
        selection=[
            ('FIX', 'Valor fijo'),
            ('PER', 'Porcentaje'),
            ('PYC', 'Fórmula')
        ]
    )
    fixed_value = fields.Float(
        string='Valor fijo',
        digits=(18, 8)
    )
    percent_value = fields.Float(
        string='Porcentaje',
        digits=(18, 2)
    )
    percent_rule = fields.Many2one(
        string='% / Regla salarial',
        comodel_name='hr.paysheet.rule',
        ondelete='cascade'
    )
    py_code = fields.Text(
        string='Fórmula',
        help=_CODE_HELP
    )
    based_on = fields.Selection(
        string='Basado en',
        required=True,
        default='ALT',
        selection=[
            ('ALT', 'Siempre verdadero'),
            ('PYC', 'Fórmula')
        ]
    )
    based_code = fields.Text(
        string='Basado en fórmula',
        help=_CODE_HELP
    )
    active = fields.Boolean(
        string='Activa',
        default=True
    )
    ignore_zero = fields.Boolean(
        string='Ignorar cero',
        default=False,
        help="Ignorar resultados igual a cero"
    )
    has_free_limit = fields.Boolean(
        string='Limite exento',
        default=False
    )
    free_limit_code = fields.Text(
        string='Fórmula exenta',
        help=_CODE_HELP
    )
    input_priority = fields.Boolean(
        string='Priorizar entrada',
        default=False,
        help="Tomar el valor de la entrada cuando haya una con el mismo concepto"
    )

    _order = 'priority ASC'

    _RULES_DICT = {}

    def reset_dict(self):
        self._RULES_DICT = {}

    def update_dict(self, _values):
        self._RULES_DICT.update(_values)

    def update_value(self, _category, _attr, _value):
        setattr(self._RULES_DICT[_category], _attr, _value)

    def check(self):

        if(self.based_on == 'ALT'):
            return True

        if(self.based_on == 'PYC'):
            try:
                eval(self.based_code, self._RULES_DICT, mode='exec', nocopy=True)
                return bool(self._RULES_DICT['result'])
            except BaseException as e:
                _logger.error("%s", str(e))
                raise UserError(_('Wrong python code defined for salary rule %s (%s).') % (self.name, self.code))

    def calculate(self):

        res = 0

        if(self.ctype == 'FIX'):

            res = self.fixed_value

        if(self.ctype == 'PER'):

            try:
                based_value = getattr(self._RULES_DICT['rules'], self.percent_rule.code)
                res = float(based_value * self.percent_value / 100)
            except Exception, e:
                _logger.error("%s", str(e))
                raise UserError(_('Wrong python code defined for salary rule %s (%s).') % (self.name, self.code))

        if(self.ctype == 'PYC'):

            try:
                eval(self.py_code, self._RULES_DICT, mode='exec', nocopy=True)
                res = float(self._RULES_DICT['result'])
            except BaseException as e:
                _logger.error("%s", str(e))
                raise UserError(_('Wrong python code defined for salary rule %s (%s).') % (self.name, self.code))

        self.update_value('rules', self.code, abs(res))

        return res

    def calculate_free_limit(self):

        res = 0

        try:
            eval(self.free_limit_code, self._RULES_DICT, mode='exec', nocopy=True)
            res = float(self._RULES_DICT['result'])
        except BaseException as e:
            _logger.error("%s", str(e))
            raise UserError('Error de fórmula exenta para la regla salarial %s (%s).' % (self.name, self.code))

        return res