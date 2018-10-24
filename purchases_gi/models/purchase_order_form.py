# -*- coding: utf-8 -*-
# © <2017> <Juan Carlos Vazquez Beas (jcvazquez@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime
import sys, logging, math
from openerp.osv import osv
from odoo import fields, models, tools, api
from openerp.exceptions import ValidationError

from .num2words import Numero_a_Texto

try:
    from num2words import num2words
except ImportError:
    logging.getLogger(__name__).warning("The num2words python library is not installed, l10n_mx_edi features won't be fully available.")
    num2words = None

_logger = logging.getLogger(__name__)

class purchase_order(models.Model):
    """
    Se heredó la clase orden de compra para adecuar la funcionalidad requerida y se agregaron campos y funciones. 
    """
    _inherit = 'purchase.order'
    _description = 'Modificaciones orden de compra'

    # _sql_constraints = [
    #    ('unique_reference', 'unique(reference)', 'El XML ya existe.')
    #]

    def get_sequence_gi(self):
        """
        Obtiene la referencia de la orden de compra.
        """
        for self_id in self:
            if self_id.is_a_purchases_order == True:
                self_id.current_sequence = self_id.sequence_order
                self_id.sequence_order = self_id.current_sequence
            else:
                self_id.current_sequence = self_id.name
                self_id.name = self_id.current_sequence

    def get_xml_no_validated(self):
        """
        Cuenta todos los xml sin registros relacionados validados.
        """
        self.get_xml_no_val = self.xml_no_ids.search_count([('order_id', '=', self.id)])

    @api.depends('order_line.invoice_lines.invoice_id')
    def _compute_invoice(self):
        """
        Obtiene las facturas relacionadas a la orden de compra
        """
        for rec in self:
            account_ids = self.env['account.invoice'].sudo().search([('origin', 'ilike', rec.name)])
            rec.invoice_ids = account_ids
            rec.invoice_count_gi = len(account_ids)


    def get_name_resum(self):
        """
        Regresa el nombre del proveedor y lo corta solo 15 caracteres, es utilizada cuando se eligen las cotizaciones. 
        """
        for self_id in self:
            self_id.partner_ref = self_id.partner_id.name[0:15]


    reception_count = fields.Integer(
        string='Entradas',
        compute=lambda self: self._reception_count()
    )
    reception_ids = fields.One2many(
        string='Entradas',
        comodel_name='purchase.reception',
        inverse_name='order_id'
    )  
    state = fields.Selection(
        selection=[
                    ('draft', 'En borrador'), 
                    ('sent', 'Solicitud de cotización'),
                    ('bid', 'Cotización recibida'),
                    ('confirmed', 'Esperando aprobación'),
                    ('to approve', 'To Approve'),   #Estados odoo Enterprise
                    ('purchase', 'Purchase Order'),   #Estados odoo Enterprise
                    # ('approve', 'Cotización aprobada'),
                    ('or_purchase_create', 'Cotización autorizada'),
                    ('related', 'Vinculada ha orden de compra'),
                    ('merged_order', 'Orden de compra fusionada'),
                    ('approved', 'Orden de compra'),
                    ('except_picking', 'Excepción de envío'),
                    ('except_invoice', 'Excepción de factura'),
                    ('done', 'Hecho'),
                    ('cancel', 'Cancelado')
                ],
        default='draft',
        help="",
        track_visibility='onchenge'
    )

    requisition_id  = fields.Many2one(
        'purchase.requisition',
        string='Solicitud de compra',
        track_visibility="onchenge"
    )


    employee_assig = fields.Many2one(
        comodel_name='hr.employee',
        string='Personal de compras asignado',
        default=lambda self: self.env.user.employee_ids,
    )

    name = fields.Char(
        string='Solicitud de cotización',
        default='En borrador',
        readonly=1
    )

    sequence_order = fields.Char(
        string='Orden de compra',
        readonly=1
    )

    sequence_cot_order = fields.Char(
        string='Cotización relacionada',
        readonly=1
    )

    create_of_draft = fields.Boolean(
        string='Se creó orden de compra directa',
    )

    is_a_purchases_order = fields.Boolean(
        string='¿Es una orden de compra?',
    )

    current_sequence = fields.Char(
        string='Referencia',
        compute=get_sequence_gi
    )

    type_origin = fields.Selection(
        string='Tipo',
        related='partner_id.origin',
        ondelete="cascade"
    )

    date_create_order = fields.Datetime(
        string='Fecha de creación',
        help="Fecha de cuando se genera la orden de compra"
    )

    boarding_ways = fields.Many2one(
        comodel_name='boarding.ways',
        string='Vía de embarque',
    )

    date_planned = fields.Datetime(
        string='Fecha prevista',
        track_visibility="onchenge",
    )

    purchase_consignee = fields.Many2one(
        comodel_name='purchase.consignee',
        string='Consignatario',
    )

    delivery_addresses = fields.Many2one(
        comodel_name='delivery.addresses',
        string='Lugar de entrega',
    )

    r_addresses = fields.Text(
        related='delivery_addresses.addresses',
        string='Domicilio de entrega',
    )

    state_order = fields.Selection(
        [('draft', 'En borrador'),
        ('generated', 'Generada'),
        ('pending', 'Pendiente'),
        ('assorted', 'Surtida'),
        ('cancel', 'Cancelada')], 
        string='Estados orden de compra',
        default='draft'
    )

    order_related = fields.Many2one(
        string='Orden padre',
        comodel_name='purchase.order',
    )

    get_xml_no_val = fields.Integer(
        string='XML no validos',
        compute='get_xml_no_validated',
    )

    xml_no_ids = fields.One2many(
        string='XMl no validos',
        comodel_name='xml.no.validated',
        inverse_name='order_id'
    )

    approved_bloq = fields.Boolean(
        string='Solicitud no aprobada',
    )

    invoice_count_gi = fields.Integer(
        string='Facturas',
        compute=_compute_invoice,
    )
    schedule_date = fields.Date(
        string='Fecha de entrega deseada',
        track_visibility='onchenge'
    )
    create_directly = fields.Boolean(
        string='Crear orden de compra directamente',
        track_visibility="onchenge"
    )
    partner_ref = fields.Char(
        string='Referencia de proveedor',
        compute=get_name_resum
    )
    use_cfdi = fields.Many2one(
        'use.cfdi',
        string='Uso de CFDI',
    )
    payment_method = fields.Selection(
        [('PUE', 'Pago en una sola exhibición'),
        ('PPD', 'Pago en parcialidades o diferido')], 
        string='Método de pago',
    )
    way_to_pay = fields.Selection(
        [('1', 'Efectivo'),
        ('2', 'Cheque nominativo'),
        ('3', 'Transferencia electrónica de fondos'),
        ('4', 'Por definir')],
        string='Forma de pago',
    )


    @api.onchange('requisition_id')
    def _onchange_requisition_id(self):
        if self.state != 'draft':
            return None

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
            if not line.description_product:
                name = line.product_id.display_name
            else:
                name = line.description_product
            if product_lang.description_purchase:
                name += '\n' + product_lang.description_purchase

            # Compute taxes
            if fpos:
                taxes_ids = fpos.map_tax(line.product_id.supplier_taxes_id.filtered(lambda tax: tax.company_id == requisition.company_id)).ids
            else:
                taxes_ids = line.product_id.supplier_taxes_id.filtered(lambda tax: tax.company_id == requisition.company_id).ids

            # Compute quantity and price_unit
            if line.product_uom_id != line.product_id.uom_po_id:
                product_qty = line.product_uom_id._compute_quantity(line.product_qty, line.product_id.uom_po_id)
                price_unit = line.product_uom_id._compute_price(line.price_unit, line.product_id.uom_po_id)
            else:
                product_qty = line.product_qty
                price_unit = line.price_unit

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
        return None


    @api.multi
    def l10n_mx_edi_amount_to_text(self, currency_id):
        """
        Convierte cantidades numéricas a palabras.
        """
        self.ensure_one()

        if not self.currency_id:
            raise ValidationError('Se debe configurar la moneda.')

        return Numero_a_Texto(self.amount_total, currency_id)


    @api.multi
    def button_cancel_gi(self):
        """
        Se sobrescribió el botón de cancelar el cual es llamado cuando se creó un registro del empleado que cánselo la orden de compra.
        """
        apag = False
        self.requisition_id.message_post('Se ha cancelado la orden de compra '+str(self.env.user.employee_ids.name))
        for line in self.requisition_id.line_ids:
            for order_ids in line.order_ids:
                if self.id == order_ids.id:
                    line.order_ids = False
                    line.state = 'draft'
                    apag = True
        if apag == True:
            reg_draft = self.env['purchase.requisition.line'].search([(
                'requisition_id', '=', self.requisition_id.id), ('state', '=', 'done')
                ])
            if len(reg_draft) > 0:
                self.requisition_id.write({'state': 'partially_authorized'})
            else:
                self.requisition_id.write({'state': 'in_progress'})
        self.button_cancel()


    @api.multi
    def action_view_invoice(self):
        """
        This function returns an action that display existing vendor bills of given purchase order ids.
        When only one found, show the vendor bill immediately.
        """
        action = self.env.ref('account.action_invoice_tree2')
        result = action.read()[0]

        #override the context to get rid of the default filtering
        result['context'] = {'type': 'in_invoice', 'default_purchase_id': self.id}

        account_ids = self.env['account.invoice'].sudo().search([('origin', 'ilike', self.name)])
        self.sudo().invoice_ids = account_ids

        if not self.invoice_ids:
            # Choose a default account journal in the same currency in case a new invoice is created
            journal_domain = [
                ('type', '=', 'purchase'),
                ('company_id', '=', self.company_id.id),
                ('currency_id', '=', self.currency_id.id),
            ]
            default_journal_id = self.env['account.journal'].search(journal_domain, limit=1)
            if default_journal_id:
                result['context']['default_journal_id'] = default_journal_id.id
        else:
            # Use the same account journal than a previous invoice
            result['context']['default_journal_id'] = self.invoice_ids[0].journal_id.id

        #choose the view_mode accordingly
        if len(self.invoice_ids) != 1:
            result['domain'] = "[('id', 'in', " + str(self.invoice_ids.ids) + ")]"
        elif len(self.invoice_ids) == 1:
            res = self.env.ref('account.invoice_supplier_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            try:
                result['res_id'] = self.invoice_ids.id
            except TypeError:
                pass

        return result
            

    def _reception_count(self):
        """
        Devuelve las entradas relacionadas a la orden de compra.
        """
        self.reception_count = self.reception_ids.search_count([('order_id', '=', self.id)])


    def wkf_bid_received(self):
        """
        Cambia de estado a la orden de compra a 'bid' además deja pasarlo si se tiene indicado que es un producto gratis.
        """
        for ord_line in self.order_line:
            if not ord_line.priceless and ord_line.price_unit <= 0.0:
                raise ValidationError('Si el producto es gratis se debe de indicar por línea de producto el campo "Sin precio".')
        self.state = "bid"


    def get_account_id_partner_id(self):
        """
        Obtiene la cuenta contable del proveedor
        """
        if self.partner_id.property_account_payable:
            return self.partner_id.property_account_payable.id
        else:
            raise ValidationError('Se debe configurar la cuenta contable del proveedor.')


    def get_account_id_product_id(self,cont):
        """
        Obtiene la cuenta contable de la categoria del producto
        """
        account_id_product_categ_id = self.order_line[cont].product_id.categ_id.property_account_expense_categ
        account_id_product = self.order_line[cont].product_id.property_account_expense

        if account_id_product:
            return account_id_product.id
        if account_id_product_categ_id:
            return account_id_product_categ_id.id
        else:
            raise ValidationError('Se debe configurar la cuenta contable del producto o en la categoria del producto.')



    @api.multi
    def complete_order_requisition(self):
        """
        Verifica que se tenga creado un diario un diario asociado a la empresa relacionada 
        a la orden de compra, y completa la orden de compra y la requisición es manda al último estado 
        además llama a la función por defecto de odoo 'button_confirm' 
        """

        account_journal = self.env['account.journal'].search([('company_id', '=', self.company_id.id),('type', '=', 'purchase')], limit=1)

        if not account_journal:
            raise ValidationError( 'No se tiene configurado un diario en la empresa, para poder recibir el xml.')

        if not self.partner_id.property_account_payable_id:
            raise ValidationError( 'No se tiene configurado la cuenta por pagar del proveedores.')


        self.date_create_order = datetime.today()

        for oreder_line_id in self.order_line:
            oreder_line_id.state_line_order = 'orden_complete'
        if self.requisition_id:
            if self.requisition_id.sudo().state == 'authorizes':
                apagador = False
                for pur in self.requisition_id.sudo().purchase_ids:
                    if pur.sudo().state == 'or_purchase_create' and pur.sudo().id != self.id:
                        apagador = True
                if apagador == False:
                    self.requisition_id.sudo().state = "done"
        self.state_order = "generated"

        for order_line_id in self.order_line:
            order_line_id.partner_id = self.partner_id


        self.state = "sent"

        for order_line in self.order_line:
            if order_line.product_id.type == 'service':
                reception = self.env['purchase.reception'].sudo().create({'name':'Pendiente de recibir','product_id': order_line.product_id.id, 'order_id': self.id, 'qty': order_line.product_qty, 'state': 'create','company_id':self.company_id.id})

        return self.sudo().button_confirm()

    @api.multi
    def authorize_order_requisition(self):
        """
        Esta función cambia de estado a cotización autorizada verifica que se coincida lo solicitado con lo cotizado 
        y lleva un control por productos además permite agregar gastos adicionales.
        """
        self.sudo()
        if self.requisition_id:
            if self.requisition_id.state == 'authorizes' or self.requisition_id.state == 'partially_authorized':
                addit_cost_cont = 0
                for ord_line in self.order_line:
                    if ord_line.additional_costs:
                        addit_cost_cont = addit_cost_cont + 1

                if addit_cost_cont == len(self.order_line):
                    pass
                else:
                    if self.create_directly or self.requisition_id.state == 'authorizes' or self.requisition_id.state == 'partially_authorized':
                        pass
                    else:
                        raise ValidationError('Solo puedes agregar gastos adicionales.  Para crear una orden de compra directa sin realizar una cotización primero debe de autorizarse.')

            else:
                raise ValidationError('No se ha autorizado la solicitud de compra.')
        else:
            raise ValidationError('No se puede crear una orden de compra sin tener una solicitud de compra.')
      

        if self.state == 'draft':
            self.sudo().create_of_draft =  True
            self.message_post('Se ha creado una orden de compra directamente por '+str(self.env.user.employee_ids.name))


            folio_sequence = self.env['ir.sequence'].sudo().search([('name', '=', 'Orden de compra'),('company_id', '=', self.company_id.id)], limit=1)
            if not folio_sequence:
                raise ValidationError('No está configurada una secuencia "Orden de compra" para la compañía.')


            self.sequence_order  = folio_sequence._next()

        self.is_a_purchases_order = True

        if self.requisition_id:
            orders_to_cancel = self.env['purchase.order'].sudo().search([('requisition_id', '=', self.requisition_id.id),('id','!=', self.id)])


        if not self.state == 'draft':
            folio_sequence = self.env['ir.sequence'].sudo().search([('name', '=', 'Orden de compra'),('company_id', '=', self.company_id.id)], limit=1)
            if not folio_sequence:
                raise ValidationError('No está configurada una secuencia "Orden de compra" para la compañía.')


            if self.state not in ('or_purchase_create', 'purchase'):
                self.sequence_order  = folio_sequence._next()
                self.sudo().sequence_cot_order = self.name
                self.sudo().name = self.sequence_order
                self.sudo().state = 'or_purchase_create'

        elif self.state == 'draft' or self.state == 'bid':

            self.sudo().sequence_cot_order = self.name
            self.sudo().name = self.sequence_order
            self.sudo().state = 'or_purchase_create'


    @api.model
    def prepare_picking_gi(self):
        """
        Prepara los pickings
        """
        if not self.group_id:
            self.group_id = self.group_id.create({
                'name': self.name,
                'partner_id': self.partner_id.id
            })
        if not self.partner_id.property_stock_supplier.id:
            raise UserError(_("You must set a Vendor Location for this partner %s") % self.partner_id.name)
        return {
            'picking_type_id': self.picking_type_id.id,
            'partner_id': self.partner_id.id,
            'date': self.date_order,
            'origin': self.name,
            'location_dest_id': self._get_destination_location(),
            'location_id': self.partner_id.property_stock_supplier.id,
            'company_id': self.company_id.id,
        }


    @api.multi
    def create_operation(self):
        """
        Crea una nueva operación con la cantidad total de la orden de compra
        """ 
        StockPicking = self.env['stock.picking']
        for order in self:
            if any([ptype in ['product', 'consu'] for ptype in order.order_line.mapped('product_id.type')]):
                pickings = order.picking_ids.filtered(lambda x: x.state not in ('done','cancel'))
                res = order.prepare_picking_gi()
                picking = StockPicking.create(res)

                moves = order.order_line.create_stock_moves_gi(picking)

                moves = moves.filtered(lambda x: x.state not in ('done', 'cancel'))._action_confirm()
                seq = 0
                for move in sorted(moves, key=lambda move: move.date_expected):
                    seq += 5
                    move.sequence = seq
                moves._action_assign()
                picking.message_post_with_view('mail.message_origin_link',
                    values={'self': picking, 'origin': order},
                    subtype_id=self.env.ref('mail.mt_note').id)
        return True

    @api.multi
    def action_view_picking(self):
        """
        This function returns an action that display existing picking orders of given purchase order ids.
        When only one found, show the picking immediately.
        """
        action = self.env.ref('stock.action_picking_tree')
        result = action.read()[0]

        #override the context to get rid of the default filtering on operation type
        result['context'] = {}
        pick_ids = self.mapped('picking_ids')
        #choose the view_mode accordingly
        if len(pick_ids) > 1:
            result['domain'] = "[('id','in',%s)]" % (pick_ids.ids)
        elif len(pick_ids) == 1:
            res = self.env.ref('stock.view_picking_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            try:
                result['res_id'] = pick_ids.id
            except TypeError:
                pass
        return result



    @api.multi
    def unlink(self):
        """
        Bloquea la eliminación de ordenes de compra.
        """
        raise ValidationError('No puedes eliminar una solicitud de compra solo cancelarla.')

    @api.model
    def create(self, vals):
        """
        Bloquea la eliminación de ordenes de compra.
        """
        result = super(purchase_order, self).create(vals)      
        folio_sequence = self.env['ir.sequence'].sudo().search([('name', '=', 'request for quotation'),('company_id', '=', result['company_id'].id)], limit=1)
        
        if 'order_line' in result:

            try:
                line_p = 0
                while len(result['order_line']) > line_p:     

                    product = self.env['product.product'].sudo().search([('id', '=', vals['order_line'][line_p][2]['product_id'])], limit=1)
                    result.message_post('Se ha agregado el producto '+str(product.name)+' por '+str(vals['order_line'][line_p][2]['product_qty'])+ ' con el precio unitario '+ str(vals['order_line'][line_p][2]['price_unit']))

                    line_p = line_p + 1

            except TypeError:
                pass



        if not folio_sequence:
            raise ValidationError('No está configurada una secuencia para la compañía. "request for quotation"') 
        result['name'] = folio_sequence._next()


        return result


    @api.multi
    def write(self,vals):
        """
        Genera un historial de cambios del precio unitario al momento de escribir el modelo.
        """
        res = super(purchase_order, self).write(vals)

        if 'order_line' in vals:
            if 'product_id' in vals or 'product_qty' in vals or 'price_unit' in vals:
                for pur_requi_gi_id in self:
                    line_pro = vals['order_line']
                    try:
                        for line_p in self.order_line:
                            pur_requi_gi_id.message_post('Se ha modificado la información del producto '+str(line_p.product_id.name)+' por '+str(line_p.product_qty)+ ' con el precio unitario '+str(line_p.price_unit))
                    except TypeError:
                        pass
        return res


    @api.multi
    def change_to_orden(self):
        # purchase_ids = self.env['purchase.order'].sudo().search([('state','=','draft'),('company_id','=',1),('create_uid','=',642)])

        # for purchase_id in purchase_ids:

        purchase_id = self


        if purchase_id.state == 'draft':
            purchase_id.create_of_draft =  True

            folio_sequence = self.env['ir.sequence'].sudo().search([('name', '=', 'Orden de compra'),('company_id', '=', purchase_id.company_id.id)], limit=1)
            if not folio_sequence:
                raise ValidationError('No está configurada una secuencia "Orden de compra" para la compañía.')


            purchase_id.sequence_order  = folio_sequence._next()

        purchase_id.is_a_purchases_order = True

        if purchase_id.requisition_id:
            orders_to_cancel = self.env['purchase.order'].sudo().search([('requisition_id', '=', purchase_id.requisition_id.id),('id','!=', purchase_id.id)])

        if not purchase_id.state == 'draft':
            folio_sequence = purchase_id.env['ir.sequence'].sudo().search([('name', '=', 'Orden de compra'),('company_id', '=', purchase_id.company_id.id)], limit=1)
            if not folio_sequence:
                raise ValidationError('No está configurada una secuencia "Orden de compra" para la compañía.')


            purchase_id.sequence_order  = folio_sequence._next()
            purchase_id.sudo().sequence_cot_order = purchase_id.name 
            purchase_id.sudo().name = purchase_id.sequence_order 
            purchase_id.state = 'or_purchase_create'

        else:


            purchase_id.sudo().sequence_cot_order = purchase_id.name 
            purchase_id.sudo().name = purchase_id.sequence_order 
            purchase_id.state = 'or_purchase_create'


    @api.multi
    def copy(self):
        """
        No se pueden duplicar ordenes de compra por que crea conflicto con los pickings y los usuarios no actualizan la información.
        """
        raise ValidationError('Por motivos de seguridad no se puede duplicar la información.')

    @api.multi
    def amount_to_text(self, amount):
        self.ensure_one()

        def _num2words(number, lang):
            try:
                return num2words(number, lang=lang).title()
            except NotImplementedError:
                return num2words(number, lang='en').title()

        if num2words is None:
            logging.getLogger(__name__).warning("The library 'num2words' is missing, cannot render textual amounts.")
            return ""

        fractional_value, integer_value = math.modf(amount)
        fractional_amount = round(abs(fractional_value), self.currency_id.decimal_places) * (math.pow(10, self.currency_id.decimal_places))
        lang_code = 'en_US'
        lang = 'en_US'
        amount_words = tools.ustr('{amt_value} {amt_word}').format(
            amt_value=_num2words(int(integer_value), lang=lang),
            amt_word=self.currency_id.currency_unit_label,
        )
        if not self.currency_id.is_zero(fractional_value):
            amount_words += ' ' + _('and') + tools.ustr(' {amt_value} {amt_word}').format(
                amt_value=_num2words(int(fractional_amount), lang=lang),
                amt_word=self.currency_id.currency_subunit_label,
            )
        return amount_words

    @api.onchange('fiscal_position_id')
    def _compute_tax_id(self):
        """
        Trigger the recompute of the taxes if the fiscal position is changed on the PO.
        """
        #for order in self:
            #order.order_line._compute_tax_id()
        _logger.info("Se quito modifcacion que elimina impuestos")

    #Permite modifcar ordenes
    change_purchase = fields.Boolean('Modificar datos de orden de compra',default=False)

    #def change_purchase_order(self):
    #    self.change_purchase = True

    #def return_purchase_order(self):
    #    self.change_purchase = False
