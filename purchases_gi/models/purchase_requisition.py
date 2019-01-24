# -*- coding: utf-8 -*-
# © <2016> <Juan Carlos VB (jcvazquez@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import date
import sys, logging
from odoo import fields, models, api, _
from openerp.exceptions import ValidationError
from .utils import redondear_cantidad_decimales
_logger = logging.getLogger(__name__)

class purchase_requisition_gi(models.Model):
    """
    Hereda el modelo de requisiciones de compra y le agrega funcionalidades necesarias para la lógica del negocio.
    """
    _inherit = 'purchase.requisition'


    def current_employee(self):
        """
        Obtiene el empleado actual (este se usará para el flujo de quien aprueba y autoriza)
        """
        if self.env.user.employee_ids:
            if len(self.env.user.employee_ids) > 1:
                raise ValidationError('Tienes mas de un empleado asociado a un usuario del ERP')
        else:
            raise ValidationError('No tienes un usuario asociado')

        return self.env.user.employee_ids.id


    def with_permissions_approve(self):
        """
        Activa un check el cual le dará permiso para aprobar.
        """
        if self.employee_approve.id == self.env.user.employee_ids.id: 
            self.with_perm_app = True

    def with_permissions_authorize(self):
        """
        Activa un check el cual le dará permiso para autorizar.
        """
        if self.employee_authorize.id == self.env.user.employee_ids.id: 
            self.with_perm_autho = True


    def get_employee_approve(self):
        """
        Obtiene el empleado que aprobara.
        """
        employee = self.env.user.employee_ids

        if len(employee) > 1:
            raise ValidationError(' Tienes mas de un empleado asociado a tu usuario del ERP')

        if employee.empl_approve:
            return employee.empl_approve

        current_job_id = (employee[0].job_id if employee else self.env['hr.job'])



        if current_job_id:
            #"Buscando empleado que aprueba"
            if employee.purchase_especial:
                return employee
            else:

                if current_job_id.category_job == 'is_director':
                    boss_of_employee = self.env['hr.employee'].search([('job_id', '=', current_job_id.job_id_boss.id)])
                    return boss_of_employee

                if current_job_id.category_job == 'is_manager':
                    boss_of_employee = self.env['hr.employee'].search([('job_id', '=', current_job_id.job_id_boss.id)])
                    return boss_of_employee

                #Jefes con gerente y jefes que pueden aprobar

                if current_job_id.category_job == 'is_boss' and current_job_id.job_id_boss.category_job != 'is_director':
                    boss_of_employee = self.env['hr.employee'].search([('job_id', '=', current_job_id.job_id_boss.id)])
                    return boss_of_employee

                if current_job_id.category_job == 'is_boss' and current_job_id.job_id_boss.category_job == 'is_director':
                    boss_of_employee = self.env['hr.employee'].search([('job_id', '=', current_job_id.job_id_boss.id)])
                    return boss_of_employee


                #Operarios y contribuidores individuales

                if current_job_id.job_id_boss.category_job == 'is_boss' and current_job_id.job_id_boss.job_id_boss.category_job != 'is_director':
                    boss_of_employee = self.env['hr.employee'].search([('job_id', '=', current_job_id.job_id_boss.job_id_boss.id)])
                    return boss_of_employee

                if current_job_id.job_id_boss.category_job == 'is_boss' and current_job_id.job_id_boss.job_id_boss.category_job == 'is_director':
                    boss_of_employee = self.env['hr.employee'].search([('job_id', '=', current_job_id.job_id_boss.id)])
                    return boss_of_employee

                if current_job_id.job_id_boss.category_job == 'is_manager' and current_job_id.job_id_boss.job_id_boss.category_job == 'is_director':
                    boss_of_employee = self.env['hr.employee'].search([('job_id', '=', current_job_id.job_id_boss.id)])
                    return boss_of_employee



    def get_employee_authorize(self):
        """
        Obtiene el empleado que autoriza. 
        """
        employee = self.env.user.employee_ids

        if employee.empl_authorize:
            return employee.empl_authorize

        if len(employee) > 1:
            raise ValidationError(' Tienes mas de un empleado asociado a tu usuario del ERP')


        current_job_id = (employee[0].job_id if employee else self.env['hr.job'])

        if employee.purchase_especial:
                return employee
        else:

            if current_job_id.category_job == 'is_director':
                boss_of_employee = self.env['hr.employee'].search([('job_id', '=', current_job_id.job_id_boss.id)])
                return boss_of_employee

            if current_job_id.category_job == 'is_manager':
                boss_of_employee = self.env['hr.employee'].search([('job_id', '=', current_job_id.job_id_boss.id)])
                return boss_of_employee

            #Jefes con gerente y jefes que pueden autoriza

            if current_job_id.category_job == 'is_boss' and current_job_id.job_id_boss.job_id_boss.category_job == 'is_director':
                boss_of_employee = self.env['hr.employee'].search([('job_id', '=', current_job_id.job_id_boss.job_id_boss.id)])
                return boss_of_employee


            if current_job_id.category_job == 'is_boss' and current_job_id.job_id_boss.category_job == 'is_director':
                boss_of_employee = self.env['hr.employee'].search([('job_id', '=', current_job_id.job_id_boss.id)])
                return boss_of_employee

            #Operarios y contribuidores individuales

            if current_job_id.job_id_boss.category_job == 'is_boss' and current_job_id.job_id_boss.job_id_boss.category_job != 'is_director':
                boss_of_employee = self.env['hr.employee'].search([('job_id', '=', current_job_id.job_id_boss.job_id_boss.job_id_boss.id)])
                return boss_of_employee

            if current_job_id.job_id_boss.category_job == 'is_boss' and current_job_id.job_id_boss.job_id_boss.category_job == 'is_director':
                boss_of_employee = self.env['hr.employee'].search([('job_id', '=', current_job_id.job_id_boss.job_id_boss.id)])
                return boss_of_employee

            if current_job_id.job_id_boss.category_job == 'is_manager' and current_job_id.job_id_boss.job_id_boss.category_job == 'is_director':
                boss_of_employee = self.env['hr.employee'].search([('job_id', '=', current_job_id.job_id_boss.job_id_boss.id)])
                return boss_of_employee


    def get_message_app(self):
        """
        Obtiene la descripción de todos los productos en las lineas de la solicitud y los muestra en la parte de descripción.
        """
        description = ''
        for line_id in self.line_ids:
            if line_id.product_id.categ_id:
                if line_id.product_id.categ_id.description_cat:
                    description + line_id.product_id.name + line_id.product_id.categ_id.description_cat+ '---------------------------------------------------------'

            if line_id.product_id.categ_id.user_requirements:
                self.message_app = "Se debe llenar y entregar al Gerente y/o Jefe de compras el formato 'Requerimientos de usuario', código: F-LCCOM1003-07."

        self.description = description


    def _allowed_dst_ids(self):
        """
        Regresa solo gerentes y directores para indicar quien usará los productos.
        """
        jobs = self.env['hr.job'].sudo().search([('category_job', 'in', ('is_manager','is_director'))])
        employees = self.env['hr.employee'].sudo().search([('job_id', 'in', [job.id for job in jobs] )])
        return [('id', 'in', [employee.id for employee in employees])]


    def get_employee_department_id(self):
        """
        Regresa el departamento actual
        """
        employee = self.env.user.employee_ids

        if len(employee) > 1:
            raise ValidationError('Tienes más de un usuario asociado al empleado actual.')

        return employee.department_id.id

    def with_perm_to_edit(self):
        """
        Verifica si se puede editar la solicitud de compra. 
        """
        if self.state == "draft":
            self.with_perm_edit = True

        if self.state == "send" and self.with_perm_app == True:
            self.with_perm_edit = True
        if self.state == "in_progress" and self.with_perm_autho == True:
            self.with_perm_edit = True

        if self.state == "approve" and self.employee_assigned.id == self.current_employee():
            self.with_perm_edit = True

    def get_current_date(self):
        """
        Regresa la fecha actual.
        """
        return date.today().strftime('%Y-%m-%d')


    def _get_picking_in(self):
        """
        No seleciona el pickin que carga por defecto.
        """
        return None

    name = fields.Char(
        string='Referencia de la solicitud de compra',
        default=' '
    )

    current_em = fields.Many2one(
        'hr.employee',
        string='Empleado actual',
        compute=current_employee,
    )

    with_perm_app = fields.Boolean(
        string='con permisos para aprobar',
        compute=with_permissions_approve,
    )


    with_perm_autho= fields.Boolean(
        string='con permisos para autorizar',
        compute=with_permissions_authorize,
    )

    with_perm_edit= fields.Boolean(
        string='con permisos para editar',
        compute=with_perm_to_edit,
        default=True
    )

    employee_purchase_reque = fields.Many2one(
        'hr.employee',
        string='Nombre del solicitante',
        default=current_employee
    )

    empl_department_id = fields.Many2one(
        'hr.department',
        string='Departamento solicitante',
        default=get_employee_department_id
    )

    company_id = fields.Many2one(
        'res.company',
        string='Compañía destino de compra',
        track_visibility="onchenge",
    )

    message_app = fields.Char(
        string='Nota:',
        compute=get_message_app
    )

    line_ids = fields.One2many(
        string='Products to Purchase',
        comodel_name='purchase.requisition.line',
        inverse_name='requisition_id',
        ondelete='cascade',
        track_visibility='onchenge'
    )

    department_id  = fields.Many2one(
        'hr.department',
        string='Departamento que lo usará',
    )

    employee_id = fields.Many2one(
        'hr.employee',
        string='Empleado que lo usará',
        domain=_allowed_dst_ids
    )

    employee_approve = fields.Many2one(
        'hr.employee',
        string='Empleado que aprueba',
        default=get_employee_approve,
        track_visibility="onchenge"
    )

    employee_authorize = fields.Many2one(
        'hr.employee',
        string='Empleado que autorizá',
        default=get_employee_authorize,
        track_visibility="onchenge"
    )

    schedule_date = fields.Date(
        string='Fecha de entrega deseada',
        track_visibility='onchenge',
        default=get_current_date
    )



    state = fields.Selection(
        [('draft','Borrador'),
        ('send', 'Enviada'),
        ('approve', 'Aprobada'),
        ('assigned', 'Asignada'),
        ('in_progress', 'En proceso'),
        ('open', 'Selección del licitador'),
        ('partially_authorized', 'Parcialmente autorizada'),
        ('authorizes', 'Autorizada'),
        ('done', 'Orden de compra'),
        ('cancel', 'Cancelado')], 
        string='¿Destino de compra?', 
        default='draft',
        required=True,
    )

    type_of_operat = fields.Selection(
        [('unit_department_or_area','Una unidad, departamento o área'),
        ('manager_or_director', 'Lo usará un gerente o director')], 
        string='Destino de compra', 
    )

    inputs_for_manufacturing = fields.Boolean(
        string='Solicitar insumo para la fabricación',
    )

    pdf1 = fields.Binary(
        string='Adjuntar PDF 1',
    )

    pdf2 = fields.Binary(
        string='Adjuntar PDF 2',
    )

    pdf3 = fields.Binary(
        string='Adjuntar PDF 3',
    )

    pdf1_filename = fields.Char(
        string='Nombre del archivo',
    )

    pdf2_filename = fields.Char(
        string='Nombre del archivo',
    )

    pdf3_filename = fields.Char(
        string='Nombre del archivo',
    )

    which_pdf = fields.Selection(
        [('is_pdf1','PDF 1'),
        ('is_pdf2', 'PDF 2'),
        ('is_pdf3', 'PDF 3')], 
        string='Seleccionar pdf', 
        default='is_pdf1',
    )

    employee_assigned = fields.Many2one(
        'hr.employee',
        string='Personal de compras asignado',
        track_visibility="onchenge"
    )

    quantity_of_product = fields.Float(
        string='Cantidad de producto',
        default=1.0
    )

    quantity_of_quotes = fields.Integer(
        string='Cantidad de cotizaciones',
    )

    to_choose_empl_apr_aut = fields.Boolean(
        string='Modificar empleados ',
        track_visibility="onchenge"
    )

    comment_cancel = fields.Text(
        string='Motivo de cancelación',
    )

    picking_type_id = fields.Many2one(
        'stock.picking.type', 
        'Operation Type',
        required=False, 
        default=_get_picking_in
    )

    urgent_buy = fields.Boolean(
        string='Compra urgente',
        track_visibility="onchenge"
    )

    urgent_mensa = fields.Text(
        string='Motivo',
        track_visibility="onchenge"
    )

    employee_destiny = fields.Many2one(
        'hr.employee',
    )

    department_destiny = fields.Many2one(
        'hr.department',
    )

    name_pr = fields.Char(
        String="Nombre de Solicitud de Compra",
        track_visibility="onchenge"
    )

    @api.onchange('schedule_date')
    def _onchange_schedule_date(self):
        """
        Verifica que no se agregue una fecha menor a la fecha actual.
        """
        if self.schedule_date < date.today().strftime('%Y-%m-%d'):
            self.schedule_date = self.get_current_date()
            return {
                'warning': {'title': "Warning", 'message': "La fecha de entrega debe ser mayor o igual a la fecha actual. De lo contrario al guardarla se establecerá la fecha actual como 'fecha deseada'."},
            }


            
    @api.onchange('requisition_id')
    def _onchange_requisition_id(self):
        """
        Se usará para recibir el artículo comprado en una ubicación diferente.
        """
        if not self.requisition_id:
            return

        requisition = self.requisition_id
        if self.partner_id:
            partner = self.partner_id
        else:
            partner = requisition.vendor_id
        payment_term = partner.property_supplier_payment_term_id
        currency = partner.property_purchase_currency_id or requisition.company_id.currency_id

        FiscalPosition = self.env['account.fiscal.position']
        fpos = FiscalPosition.get_fiscal_position(partner.id)
        fpos = FiscalPosition.browse(fpos)

        self.partner_id = partner.id
        self.fiscal_position_id = fpos.id
        self.payment_term_id = payment_term.id,
        self.company_id = requisition.company_id.id
        self.currency_id = currency.id
        self.origin = requisition.name
        self.partner_ref = requisition.name # to control vendor bill based on agreement reference
        self.notes = requisition.description
        self.date_order = requisition.date_end or fields.Datetime.now()
        self.picking_type_id = requisition.picking_type_id.id

        if requisition.type_id.line_copy != 'copy':
            return

        # Create PO lines if necessary
        order_lines = []
        for line in requisition.line_ids:
            # Compute name
            product_lang = line.product_id.with_context({
                'lang': partner.lang,
                'partner_id': partner.id,
            })
            name = product_lang.display_name
            if product_lang.description_purchase:
                name += '\n' + product_lang.description_purchase

            # Compute taxes
            if fpos:
                taxes_ids = fpos.map_tax(line.product_id.supplier_taxes_id.filtered(lambda tax: tax.company_id == requisition.company_id)).ids
            else:
                taxes_ids = line.product_id.supplier_taxes_id.filtered(lambda tax: tax.company_id == requisition.company_id).ids

            # # Compute quantity and price_unit
            # if line.product_uom_id != line.product_id.uom_po_id:
            #     product_qty = line.product_uom_id._compute_quantity(line.product_qty, line.product_id.uom_po_id)
            #     price_unit = line.product_uom_id._compute_price(line.price_unit, line.product_id.uom_po_id)
            # else:
            #     product_qty = line.product_qty
            #     price_unit = line.price_unit

            if requisition.type_id.quantity_copy != 'copy':
                product_qty = 0

            # Compute price_unit in appropriate currency
            if requisition.company_id.currency_id != currency:
                price_unit = requisition.company_id.currency_id.compute(price_unit, currency)

            # Create PO line
            order_line_values = line._prepare_purchase_order_line(
                name=name, product_qty=product_qty, price_unit=price_unit,
                taxes_ids=taxes_ids)
            order_lines.append((0, 0, order_line_values))
        self.order_line = order_lines



    @api.multi
    def analyze_quotes(self):
        """
        Envía a analizar las cotizaciones y verifica que exista alguna en estado recibido.
        """
        yes_to_coti = False
        if len(self.purchase_ids) == 1:
            if self.purchase_ids.create_directly:
                yes_to_coti = True

        if self.purchase_ids:
            for purchase_id in self.purchase_ids:
                _logger.warning(purchase_id.state)
                purchase_id.approved_bloq =  True
                if purchase_id.state in ('bid','confirmed','approved'):
                    yes_to_coti = True
            
            if yes_to_coti == False:
                raise ValidationError('Se debe tener al menos una cotización en estado "Cotización recibida" para su autorización.')

            self.quantity_of_quotes = len(self.purchase_ids)
            template = self.env['mail.template'].search([('name', '=', 'analyze purchase requisition')], limit=1)

            template.send_mail(self.id, force_send=True)

            self.state = 'in_progress'
        else:
            raise ValidationError('Se debe tener al menos una cotización en estado "Cotización recibida" para su autorización.')


    @api.multi
    def cancel_purcha_requisition(self):
        """
        Cambia de estado a cancelada.
        """
        self.state = 'cancel'


    @api.multi
    def assign_auxiliary(self):
        """
        Verifica que se asocie un auxiliar de compras y le envía un correo
        """
        if not self.employee_assigned:
            raise ValidationError('Se debe de asignar el personal de compras asignado.')

        template = self.env['mail.template'].search([('name', '=', 'assigned purchase requisition')], limit=1)
        
        self.state = 'assigned'

        template.send_mail(self.id, force_send=True)



    @api.onchange('product_id')
    def onchange_product_id(self):
        """
        Muestra un mensaje del formato 'Requerimientos de usuario'
        """
        if self.product_id:
            self.description = self.product_id.categ_id.description_cat
            self.description_product = self.product_id.display_name
            if self.product_id.categ_id.user_requirements:
                self.message_app = "Se debe llenar y entregar al Gerente y/o Jefe de compras el formato 'Requerimientos de usuario', código: F-LCCOM1003-07."


    @api.onchange('type_of_operat')
    def onchange_type_of_operat(self):
        """
        Muestra un mensaje del número de proyecto
        """
        if self.type_of_operat:
            self.department_id = False
            self.employee_id = False

            employee = self.env.user.employee_ids

            current_job_id = (employee[0].job_id if employee else self.env['hr.job'])

            if current_job_id:
                if current_job_id.department_id.project_development:
                    self.message_app = "Se debe indicar el número de proyecto o desarrollo en TERMINOS Y CONDICIONES."


    @api.multi
    def send_request_purchanse(self):
        """
        Envía la solicitud de compras y verifica si es un insumo y si se ha elegido una compañía correcta.
        """
        if not self.line_ids:
            raise ValidationError('Upps se te ha olvidado agregar el producto a solicitar :)')

        if not self.company_id.vat:
            raise ValidationError('Se debe elegir una "Compañía destino de compra" correcta.')


        if not self.inputs_for_manufacturing:
            for line_id in self.line_ids:
                if line_id.product_id.inputs_for_manufacturing:
                    raise ValidationError('Es necesario tener activado el casilla de verificación "Solicitar insumo para la fabricación". Si no es visible en su pantalla no está autorizado para solicitar un insumo.')


        line_ids = []       

        self.multiple_rfq_per_supplier = True

        if self.department_id:
            self.account_analytic_id = self.department_id.hr_busi_segme.id

        employee = self.env.user.employee_ids


        self.state = 'send'
        template = self.env['mail.template'].search([('name', '=', 'purchase requisition send')], limit=1)

        template.send_mail(self.id, force_send=True)
        
        self.message_post('Se ha enviado a aprobar una solicitud por el empleado '+str(self.env.user.employee_ids.name))
    


    @api.multi
    def request_purchanse_approve(self):
        """
        Envía a aprobar la solicitud de compra y envía correos a los empleados involucrados.
        """
        template_approve = self.env['mail.template'].search([('name', '=', 'purchase requisition approve')], limit=1)
        template_boss_purchase = self.env['mail.template'].search([('name', '=', 'boss purchase requisition authorizes')], limit=1)

        template_approve.sudo().send_mail(self.id, force_send=True)
        template_boss_purchase.sudo().send_mail(self.id, force_send=True)

        self.state = 'approve'


    @api.multi
    def request_purchanse_authorization(self, transfer_inmediate = False):
        """
        Busca las cotizaciones que existen en la solicitud de compra 
        y verifica los totales para que cuadren las cantidades.
        """
        self.sudo()
        template_auth_emplo = self.env['mail.template'].search([('name', '=', 'applicant of purchase already authorized')], limit=1)
        template_auth_empl_approve = self.env['mail.template'].search([('name', '=', 'purchase requisition to approve authorizes')], limit=1)

        template_auth_emplo.send_mail(self.id, force_send=True)

        template_auth_empl_approve.send_mail(self.id, force_send=True)

        lines_id = self.env['purchase.requisition.line'].search([('requisition_id', '=', self.id), ('order_ids', '!=', False), ('state', '=', 'draft')])

        if len(lines_id) == 0:
            raise ValidationError(
                "No tienen ninguna linea con cotizacion asignada y pendiente de autorizar. ")

        lines_id_authorizes = self.env['purchase.requisition.line'].search(
            [('requisition_id', '=', self.id), ('order_ids', '!=', False), ('state', 'in', ['draft', 'done'])])
        lines_id_total = self.env['purchase.requisition.line'].search(
            [('requisition_id', '=', self.id), ('state', 'in', ['draft', 'done'])])


        if len(lines_id_authorizes) == len(lines_id_total):
            self.write({'state': 'authorizes'})
        else:
            self.write({'state': 'partially_authorized'})

        for line_id in self.line_ids:
            if line_id.order_ids and line_id.state == 'draft':
                line_id.state = 'done'
                qty_quoted_for = redondear_cantidad_decimales(line_id.product_qty_quoted)
                if line_id.product_qty < qty_quoted_for:
                    raise ValidationError('La cantidad total cotizado es mayor a lo requerido. Favor de verificar la cotización para el producto "'+ line_id.product_id.name+'"')

                #Busca las cotizaciones que existen en la solicitud de compra
                for order_id in line_id.order_ids:
                    no_product = False
                    for order_line_id in order_id.order_line:

                        if line_id.product_id == order_line_id.product_id and line_id.account_analytic_id == order_line_id.account_analytic_id:
                            no_product = True

                        req_line = self.env['purchase.requisition.line'].sudo().search([('requisition_id', '=', self.id),('product_id', '=', order_line_id.product_id.id),('order_ids', 'in', order_line_id.order_id.id)])


                        if not req_line and order_line_id.additional_costs == False:
                            raise ValidationError('Debes de administrar las cotizaciones para que coincida con lo solicitado. Del proveedor --> '+ order_line_id.order_id.partner_id.name)


                        if order_line_id.order_id.state == 'cancel':
                            raise ValidationError("La orden de compra o cotización fue cancelada anteriormente. --> "+order_line_id.order_id.name)
                        else:
                             order_line_id.order_id.sudo().authorize_order_requisition()

                    if not no_product:
                        raise ValidationError("No se tiene una cotización para el producto {} y la cuenta analitica: {} ".format(line_id.product_id.name, line_id.account_analytic_id.name))

        for purchase_id in self.purchase_ids:
            purchase_id.sudo().approved_bloq = False

        if len(self.purchase_ids) == 1:
            if self.purchase_ids.create_directly:
                self.purchase_ids.sudo().authorize_order_requisition()


    @api.model
    def create(self, vals):
        """
        Agrega log de modificaciones y crea las secuencias por compañías.
        """
        result = super(purchase_requisition_gi, self).create(vals)
        company_id = self.env['res.company'].sudo().search([('id', '=', vals['company_id'])], limit=1)

        if not company_id.vat:
            raise ValidationError('La empresa seleccionada no es correcta. favor de verificarla.')

        line_ids = []
        folio_sequence = self.env['ir.sequence'].sudo().search([('name', '=', 'purchase_requisition'),('company_id', '=', vals['company_id'])], limit=1)

        if 'line_ids' in vals:

            try:
                line_p = 0
                while len(vals['line_ids']) > line_p:     

                    product = self.env['product.product'].sudo().search([('id', '=', vals['line_ids'][line_p][2]['product_id'])], limit=1)
                    result.message_post('Se ha agregado el producto '+str(product.name)+' con la cantidad '+str(vals['line_ids'][line_p][2]['product_qty']))

                    line_p = line_p + 1

            except TypeError:
                pass

        if not folio_sequence:
            raise ValidationError('No está configurada una secuencia para la compañía. "purchase_requisition"')
        result['name'] = folio_sequence._next()

        return result


    @api.multi
    def write(self,vals):
        """
        Agrega log de modificaciones y crea las secuencias por compañías.
        """
        res = super(purchase_requisition_gi, self).write(vals)

        if 'line_ids' in vals:
            for pur_requi_gi_id in self:
                line_pro = vals['line_ids']
                try:
                    for line_p in self.line_ids:
                        pur_requi_gi_id.message_post(' '+str(line_p.product_id.name)+' con la cantidad  '+str(line_p.product_qty))
                except TypeError:
                    pass

        return res

    @api.multi
    def unlink(self):
        """
        No permite eliminar requisiciones si no están en estado borrador.
        """
        for self_id in self:
            if self_id.state != 'draft':
                raise ValidationError('No puedes eliminar una solicitud de compra solo cancelarla.')

        return super(purchase_requisition_gi, self).unlink()



    def get_product_one(self):
        """
        Metodo para obtener de las lineas 1 de los productos que tenga registrados
        :return:
        """
        for rec in self:
            if rec.line_ids:
                rec.product_id = rec.line_ids[0].product_id.id

    product_id = fields.Many2one(
        'product.product',
        string='Producto',
        compute=get_product_one
    )

    def get_vendor_one(self):
        """
        Metodo para obtener de la solicitud de cotizacion u orden de compra el proveedor
        :return:
        """
        for rec in self:
            if rec.purchase_ids:
                rec.vendor_quotation_id = rec.purchase_ids[0].partner_id.id


    vendor_quotation_id = fields.Many2one('res.partner', string="Proveedor", compute=get_vendor_one)


    @api.multi
    def action_cancel(self, context=False):
        # try to set all associated quotations to cancel state
        for requisition in self:
            if context != True:
                for line_id in requisition.line_ids:
                    if not line_id.order_ids and line_id.state == 'draft':
                        view = self.env.ref('purchases_gi.view_cancel_line')
                        wiz = self.env['purchase.inmediate.transfer'].create({'purchase_ids': [(4, self.id)]})
                        return {
                            'name': _('Lineas sin asignar cotizacion?'),
                            'type': 'ir.actions.act_window',
                            'view_type': 'form',
                            'view_mode': 'form',
                            'res_model': 'purchase.inmediate.transfer',
                            'views': [(view.id, 'form')],
                            'view_id': view.id,
                            'target': 'new',
                            'res_id': wiz.id,
                            'context': self.env.context,
                        }
            elif context == True:
                reg_cancel = self.env['purchase.requisition.line'].search([(
                    'requisition_id', '=', requisition.id), ('state', '=', 'cancel')
                ])
                if len(reg_cancel) == len(requisition.line_ids):
                    requisition.write({'state': 'cancel'})
                    for po in requisition.purchase_ids:
                        po.message_post(body=_('Cancelled by the agreement associated to this quotation.'))
                else:
                    reg_draft = self.env['purchase.requisition.line'].search([(
                        'requisition_id', '=', requisition.id), ('state', '=', 'draft')
                    ])
                    if len(reg_draft) > 0:
                        requisition.write({'state': 'partially_authorized'})
                    else:
                        apag = False
                        for line_id in requisition.line_ids:
                            if line_id.state == 'done':
                                for purch in line_id.purchase_ids:
                                    if purch.state not in ('purchase','cancel'):
                                        apag = True
                                        break
                        if apag == True:
                            requisition.write({'state': 'authorizes'})
                        else:
                            requisition.write({'state': 'done'})
                return
            raise ValidationError('No hay ninguna linea que se pueda cancelar')

    @api.onchange('empl_department_id')
    def _onchange_empl_department_id(self):
        if self.empl_department_id:
            self.employee_assigned = self.empl_department_id.employee_assigned.id

    @api.depends('employee_assigned')
    def _compute_employe(self):
        for rec in self:
            rec.ensure_one()
            rec.user_id_employee_assigned = rec.employee_assigned.user_id

    user_id_employee_assigned = fields.Many2one('res.users', compute=_compute_employe, store=True, string= "Personal de compras asignado")

    def _compute_with_perm_purchasemanager(self):
        for group_id in self.env.user.groups_id:
            if group_id.id == 36:
                self.with_perm_purchasemanager = True
                return 
        self.with_perm_purchasemanager = False
    
    with_perm_purchasemanager = fields.Boolean('Permiso de responsable', default=False, compute=_compute_with_perm_purchasemanager)

    @api.depends('with_perm_purchasemanager', 'with_perm_app', 'with_perm_autho', 'state')
    def _compute_with_perm_cancel_requisition(self):
        if self.with_perm_purchasemanager == False and self.with_perm_app == False and self.with_perm_autho == False:
            self.with_perm_cancel_requisition = False
            return
        else:
            if self.state in ('cancel', 'done', 'authorizes'):
                self.with_perm_cancel_requisition = False
            else:
                self.with_perm_cancel_requisition = True

    with_perm_cancel_requisition = fields.Boolean('Permiso de cancelar', default=False, compute=_compute_with_perm_cancel_requisition)