# -*- coding: utf-8 -*-
# © <2016> <Omar Torres Silva (otorres@grupoifaco.com.mx) >
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime, timedelta
import logging
import os
import re
import requests

from openerp import fields, models, api
from openerp.exceptions import ValidationError
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT

from hr_paysheet import PaysheetTools

_logger = logging.getLogger(__name__)

class hr_employee_gi(models.Model):
    _inherit = 'hr.employee'

    PAYMENT_PERIODS = {
        'S': 'Semanal',
        'Q': 'Quincenal',
        'M': 'Mensual'
    }

    @api.multi
    def _total_holidays(self):

        for item in self:
            expired_holidays = sum(line.expired_holidays if line.state == 'ok' else 0 for line in item.holidays_ids)
            item.total_holidays = (item.available_holidays + expired_holidays) - item.taken_holidays

    @api.multi
    def _expired_holidays(self):

        for item in self:
            item.expired_holidays = sum(line.expired_holidays if line.state == 'ok' else 0 for line in item.holidays_ids)


    old_id = fields.Integer(
        string='ID de empleado'
    )
    history_id = fields.Integer(
        string='ID Histórico'
    )
    paysheet_count = fields.Integer(
        string='Nóminas',
        compute=lambda self: self._compute_paysheet_count()
    )
    paysheet_ids = fields.One2many(
        string='Nóminas',
        comodel_name='hr.paysheet',
        inverse_name='employee_id'
    )
    employer_registration = fields.Many2one(
        string='Registro patronal',
        comodel_name='hr.employer.registration'
    )
    employer_place = fields.Char(
        string='Domicilio del patrón',
        related='employer_registration.place'
    )
    ssn = fields.Char(
        string='Número de afiliación'
    )
    umf = fields.Char(
        string='UMF',
        help='Unidad Médica Familiar',
        size=6
    )
    sua_state_id = fields.Many2one(
        string='Lugar de nacimiento SUA',
        comodel_name='hr.sua.state'
    )
    zip_code = fields.Char(
        string='Código postal',
        size=5
    )
    curp = fields.Char(
        string='CURP'
    )
    rfc = fields.Char(
        string='RFC'
    )
    cel_phone = fields.Char(
        string='Teléfono particular',
    )
    alt_phone = fields.Char(
        string='Teléfono recados',
    )
    wage_type = fields.Selection(
        string='Tipo de salario',
        default='2',
        selection=[
            ('0', 'Fijo'),
            ('1', 'Variable'),
            ('2', 'Mixto')
        ]
    )
    in_date = fields.Date(
        string='Fecha de ingreso'
    )
    out_date = fields.Date(
        string='Fecha de baja'
    )
    reg_date = fields.Date(
        string='Fecha de alta'
    )
    ss_in_date = fields.Date(
        string='Alta en el IMSS'
    )
    ss_out_date = fields.Date(
        string='Baja en el IMSS'
    )
    discount_food = fields.Boolean(
        default=True,
        string='Descuento de comida'
    )
    street = fields.Char(
        string='Domicilio'
    )
    suburb = fields.Char(
        string='Colonia / Población'
    )
    city_id = fields.Many2one(
        string='Ciudad / Municipio',
        comodel_name='res.country.city'
    )
    work_state_id = fields.Many2one(
        string='Lugar de trabajo',
        comodel_name='res.country.state',
        help="""Último estado donde trabajó el periodo de nómina,
en caso de haber trabajado en varios estados
indicar el estado donde trabajó mas tiempo."""
    )
    mother_lives = fields.Boolean(
        string='Vive la mamá'
    )
    mother_name = fields.Char(
        string='Nombre de la mamá'
    )
    father_lives = fields.Boolean(
        string='Vive el papá'
    )
    father_name = fields.Char(
        string='Nombre del papá'
    )
    blood_type = fields.Selection(
        string='Tipo de sangre',
        selection=[
            ('AP', 'A +'),
            ('AN', 'A -'),
            ('BP', 'B +'),
            ('BN', 'B -'),
            ('ABP', 'AB +'),
            ('ABN', 'AB -'),
            ('OP', 'O +'),
            ('ON', 'O -'),
            ('DE', 'Desconocido')
        ]
    )
    emergency_name = fields.Char(
        string='Contacto'
    )
    emergency_phone = fields.Char(
        string='Teléfono'
    )
    in_date = fields.Date(
        string='Fecha de antigüedad'
    )
    academic_level_id = fields.Many2one(
        string='Máximo grado escolar',
        comodel_name='hr.academic.level'
    )
    academic_situation = fields.Selection(
        string='Situación académica',
        selection=[
            ('TE', 'Terminó'),
            ('NT', 'No terminó')
        ]
    )
    profession_id = fields.Many2one(
        string='Profesión',
        comodel_name='hr.profession'
    )
    academic_institution_id = fields.Many2one(
        string='Institución académica',
        comodel_name='hr.academic.institution'
    )
    study_title_id = fields.Many2one(
        string='Constancia de estudio',
        comodel_name='hr.study.title'
    )
    labor_union = fields.Boolean(
        string='Es sindicalizado'
    )
    payment_type = fields.Selection(
        string='Tipo de pago',
        default='E',
        selection=[
            ('D', 'Deposito en banco'),
            ('E', 'Efectivo'),
            ('O', 'Otro')
        ]
    )
    clabe_account = fields.Char(
        string='Cuenta CLABE',
        size=18
    )
    work_type = fields.Selection(
        string='Tipo de jornada',
        default='01',
        size=2,
        selection=[
            ('01','Diurna'),
            ('02','Nocturna'),
            ('03','Mixta'),
            ('04','Por hora'),
            ('05','Reducida'),
            ('06','Continuada'),
            ('07','Partida'),
            ('08','Por turnos'),
            ('99','Otra Jornada')
        ]
    )
    has_check = fields.Boolean(
        string='No verificar checadas',
        help="""Cuando el empleado tenga marcado este campo
a la hora de procesar la nómina se le asignará directamente
el número de días trabajados correspondiente al periodo de pago
sin consultar los regitros de asistencia"""
    )
    marital_state = fields.Selection(
        string='Estado civil',
        size=3,
        selection=[
            ('SOL', 'Soltero(a)'),
            ('CAS', 'Casado(a)'),
            ('VIU', 'Viudo(a)'),
            ('DIV', 'Divorciado(a)'),
            ('SEP', 'Separado(a)'),
            ('UNL', 'Unión libre'),
        ]
    )
    emp_gender = fields.Selection(
        string='Género',
        size=1,
        selection=[
            ('H', 'Masculino'),
            ('M', 'Femenino')
        ]
    )
    segment_id = fields.Many2one(
        string='Segmento de negocio',
        comodel_name='hr.business.segment'
    )
    expense_id = fields.Many2one(
        string='Gasto contable',
        comodel_name='hr.account.expense'
    )
    bank_account = fields.Char(
        string='Cuenta de banco'
    )
    bank_id = fields.Many2one(
        string='Banco',
        comodel_name='res.bank'
    )
    contract_regime_id = fields.Many2one(
        string='Régimen de contratación',
        comodel_name='hr.contract.regime'
    )
    sua_name = fields.Char(
        string='Nombre SUA'
    )
    worker_type = fields.Selection(
        string='Tipo de trabajador',
        size=1,
        default='1',
        selection=[
            ('1', 'Permanente'),
            ('2', 'Eventual'),
            ('3', 'Construcción'),
            ('4', 'Eventuales del campo')
        ]
    )
    week_type = fields.Selection(
        string='Jornada/Semana Reducida',
        size=1,
        default='0',
        selection=[
            ('0', 'Semana Completa'),
            ('1', '1 Día'),
            ('2', '2 Días'),
            ('3', '3 Días'),
            ('4', '4 Días'),
            ('5', '5 Días'),
            ('6', 'Menor a 8 Horas')
        ]
    )
    pensioner = fields.Selection(
        string='Pensionado',
        size=1,
        default='1',
        selection=[
            ('1', 'Sin Pensión'),
            ('2', 'Pensión IV'),
            ('3', 'Pensión CV')
        ]
    )
    payment_period = fields.Selection(
        string='Periodicidad de pago',
        default='S',
        size=15,
        selection=[
            ('S', 'Semanal'),
            ('Q', 'Quincenal'),
            ('M', 'Mensual')
        ]
    )
    read_company_name = fields.Char(
        string='Empresa',
        compute=lambda self: self._compute_read_company_name()
    )
    has_medical_insurance = fields.Boolean(
        string='Seguro de gastos médicos',
        default=False
    )
    medical_insurance = fields.Float(
        string='Prima de seguro'
    )
    holidays_ids = fields.One2many(
        string='Vacaciones',
        comodel_name='hr.holidays.line',
        inverse_name='employee_id'
    )
    last_anniversary = fields.Date(
        string='Último aniversario',
        help='Último aniversario en la empresa'
    )
    anniversary = fields.Integer(
        string='Aniversario No.',
        help='Número de aniversario en la empresa'
    )
    available_holidays = fields.Integer(
        string='Cumplidas'
    )
    taken_holidays = fields.Integer(
        string='Tomadas'
    )
    total_holidays = fields.Integer(
        string='Disponibles',
        compute=_total_holidays
    )
    expired_holidays = fields.Integer(
        string='Vacaciones vencidas',
        compute=_expired_holidays
    )
    vehicle_id = fields.Many2one(
        string='Vehículo asignado',
        comodel_name='fleet.vehicle'
    )
    ignore_ptu = fields.Boolean(
        string='No considerar en P.T.U.',
        default=False
    )
    ignore_bp = fields.Boolean(
        string='No considerar en B.P.',
        default=False,
        help='No considerar empleado en bono de productividad'
    )
    beneficiary_code = fields.Char(
        string='ID Beneficiario',
        size=12
    )
    is_current_employee = fields.Boolean(
        string='Usuario actual',
        compute=lambda self: self._compute_current_employee()
    )
    housing_credit = fields.Char(
        string='Número de crédito',
        size=10
    )
    credit_type = fields.Selection(
        string='Tipo de crédito',
        size=1,
        selection=[
            ('1', 'Porcentaje'),
            ('2', 'Cuota Fija'),
            ('2', 'Veces S.M.')
        ]
    )
    credit_discount = fields.Float(
        string='Valor de descuento',
        digits=(16, 2)
    )
    start_credit = fields.Date(
        string='Fecha inicio'
    )
    boss_id = fields.Many2one(
        string='Jefe',
        comodel_name='hr.employee'
    )
    birth_date = fields.Date(
        string='Fecha de nacimiento'
    )
    cfdi_mail = fields.Char(
        string='Correo CFDI',
        size=120
    )
    cfdi_send = fields.Boolean(
        string='Enviar CFDI'
    )
    cfdi_mail_ok = fields.Boolean(
        string='Validado'
    )
    cfdi_mail_token = fields.Integer(
        string='Token CFDI'
    )

    def _compute_paysheet_count(self):

        for item in self:
            item.paysheet_count = item.sudo().paysheet_ids.search_count([('employee_id', '=', item.id)])

    def _compute_read_company_name(self):

        for item in self:
            item.read_company_name = item.company_id.name

    @api.model
    def create(self, vals):
        rec = super(hr_employee_gi, self).create(vals)

        self.env.cr.execute("""
            DELETE FROM mail_followers WHERE res_model = 'hr.employee';
            DELETE FROM mail_message WHERE model = 'hr.employee';
        """)

        return rec

    @api.multi
    def write(self, vals):

        if 'company_id' in vals.keys():

            if vals['company_id'] != self.company_id.id:

                _logger.debug("COMPANY CHANGE E: %s, U: %s, O: %s, N: %s", self.name, self.env.uid, self.company_id.id, vals['company_id'])

        res = super(hr_employee_gi, self).write(vals)

        for contract in self.contract_ids:
            contract.job_id = self.job_id.id

        return res

    @api.multi
    def generate_old_id(self):

        if not self.company_id.id:
            self.old_id = 0
            return

        if not self.company_id.short_name:
            self.old_id = 0
            return

        self.env.cr.execute("""
            SELECT max(old_id) FROM hr_employee he INNER JOIN resource_resource rr ON he.resource_id = rr.id WHERE rr.company_id = %s
        """ % self.company_id.id)

        last_key = self.env.cr.fetchone()[0]

        self.old_id = last_key + 1 if last_key else 1

    @api.onchange('children')
    def check_change(self):

        if self.children > 100:

            raise ValidationError("El campo número de hijos no puede ser mayor a 100")

    @api.onchange('user_id')
    def _onchange_user(self):
        self.work_email = self.user_id.email

    @api.onchange('credit_number')
    def credit_number_change(self):

        if not self.credit_number:
            return

        if len(self.credit_number) != 10:
            raise ValidationError("Longitud de número incorrecta")

        try:
            control_num = int(self.credit_number[:2])
        except Exception as e:
            raise ValidationError("Error de formato")

        if not (control_num >= 1 and control_num <= 32) and not control_num > 72:
            raise ValidationError("El formato de número no corresponde con la rutina proporcionada por el INFONAVIT")

    @api.one
    @api.constrains('ssn')
    def _check_ssn(self):

        if(not self.ssn):
            return

        if len(self.ssn) > 11:

            raise ValidationError("El campo Número de seguro social no puede tener una longitud mayor a 11 caracteres")

    @api.one
    @api.constrains('curp')
    def _check_curp(self):

        if(not self.curp):
            return

        if len(self.curp) > 18:

            raise ValidationError("El campo CURP no puede tener una longitud mayor a 18 caracteres")

    @api.one
    @api.constrains('rfc')
    def _check_rfc(self):

        if(not self.rfc):
            return

        if len(self.rfc) > 13:

            raise ValidationError("El campo RFC no puede tener una longitud mayor a 13 caracteres")

    @api.onchange('company_id')
    def company_id_change(self):

        self.employer_registration = False

    @api.onchange('cfdi_mail')
    def check_change_cfdi_mail(self):

        self.cfdi_mail_ok = False

    @api.onchange('has_medical_insurance')
    def has_medical_insurance_change(self):

        if self.has_medical_insurance and self.birth_date:

            os.environ['TZ'] = "America/Mexico_City"

            from_date = datetime.strptime(self.birth_date, DEFAULT_SERVER_DATE_FORMAT)
            to_date = datetime.today()

            years = int((to_date - from_date).days / 365)

            for row in self.env['hr.medical.insurance'].search([]):

                if (years >= row.from_years) and (years <= row.to_years):

                    self.medical_insurance = row.male if self.emp_gender == 'H' else row.female
                    return

        else:
            self.medical_insurance = 0


    @api.multi
    def update_holidays(self):

        # CONFIG
        holidays_table_code = 'EMPLOYEE_HOLIDAYS'
        holidays_concepts = '36,65'

        if not self.in_date:
            return

        if not self.last_anniversary:
            self.last_anniversary = self.last_anniversary_date()

        today = datetime.today()
        in_date = datetime.strptime(self.in_date, DEFAULT_SERVER_DATE_FORMAT)
        from_date = datetime.strptime(self.last_anniversary, DEFAULT_SERVER_DATE_FORMAT)
        to_date = in_date.replace(year=from_date.year + 1)
        pstools = PaysheetTools()
        years = pstools.trunc_decimals((today - in_date).days / 365.25, 2)

        # UPDATE LAST ANIVERSARY
        self.last_anniversary = self.last_anniversary_date()

        # CLOSE HOLIDAYS LINE
        if to_date.date() == today.date():

            if self.total_holidays > 0:

                line = self.env['hr.holidays.line'].search([
                    ('employee_id', '=', self.id),
                    ('from_date', '=', from_date.date()),
                    ('to_date', '=', to_date.date())
                ], limit=1)

                if not line:

                    line = self.env['hr.holidays.line'].create({
                        'employee_id': self.id,
                        'from_date': from_date.date(),
                        'to_date': to_date.date(),
                        'expired_holidays': self.total_holidays,
                        'year_num': self.anniversary
                    })

                self.last_anniversary = to_date.date()

        # UPDATE ANIVERSARY NUM
        self.anniversary = int(years)

        # UPDATE AVAILABLE HOLIDAYS
        table = self.env['hr.rank.table'].sudo().search([('code', '=', holidays_table_code)], limit=1)
        row = table.self_find(years) if table else False
        self.available_holidays = 0 if not table or not row else row.fixed_amount

        # UPDATE TAKEN DAYS
        self.env.cr.execute("""
            SELECT COALESCE(SUM(ABS(pt.amount)), 0)
            FROM hr_paysheet_trade pt
            INNER JOIN hr_paysheet_concept pc ON pt.concept_id = pc.id
            INNER JOIN hr_paysheet hp ON pt.paysheet_id = hp.id
            INNER JOIN hr_paysheet_lot hpl ON hp.lot_id = hpl.id
            WHERE hpl.payment_date >= '%s' AND hpl.payment_date <= '%s'
            AND hp.employee_id = %s
            AND pc.code IN (%s)
        """ % (
            self.last_anniversary,
            to_date.date(),
            self.id,
            holidays_concepts
        ))

        self.taken_holidays = self.env.cr.fetchone()[0]

    @api.model
    def update_holidays_cron(self):

        _logger.debug("INICIO => ACTUALIZAR VACACIONES")

        for employee in self.search([]):

            employee.update_holidays()

        _logger.debug("TERMINA => ACTUALIZAR VACACIONES")

    def last_anniversary_date(self, _to_date = False):

        to_date = datetime.strptime(_to_date, DEFAULT_SERVER_DATE_FORMAT) if _to_date else datetime.today()
        in_date = datetime.strptime(self.in_date, DEFAULT_SERVER_DATE_FORMAT)

        return in_date.replace(year=to_date.year) if to_date.date() >= in_date.replace(year=to_date.year).date() else in_date.replace(year=to_date.year - 1)

    @api.onchange('rfc')
    def _check_rfc(self):

        exp = re.compile(r'\b[a-zA-Z]{4}[0-9]{6}[a-zA-Z0-9]{3}\b')

        if not self.rfc:
            return

        if not exp.search(self.rfc):
            raise ValidationError("Formato de RFC invalido.")

    def _compute_current_employee(self):

        for item in self:
            item.is_current_employee = self.env.uid == item.user_id.id

    def antique_years(self, _date = datetime.today(), _precision = 2):

        from_date = datetime.strptime(self.in_date, DEFAULT_SERVER_DATE_FORMAT)
        to_date = datetime.strptime(_date, DEFAULT_SERVER_DATE_FORMAT) if type(_date) is str else _date
        to_date = to_date + timedelta(days=1)
        years = (to_date - from_date).days / 365.25

        return PaysheetTools().trunc_decimals(years, _precision) if _precision > 0 else years