# -*- coding: utf-8 -*-
# © <2017> <Juan Carlos Vazquez Beas (jcvazquez@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import sys, logging
from datetime import date
from odoo import fields, models, api
from openerp.osv import osv
from openerp.exceptions import ValidationError
import openerp.addons.decimal_precision as dp


_logger = logging.getLogger(__name__)

class purchase_reception(models.Model):
    """
    Se agregó el modelo de recepciones por qué por control interno es necesario.
    """
    _name = 'purchase.reception'
    _inherit = ['mail.thread']


    def get_name_resum(self):
        """
         Agrega diferentes campos para que se puedan visualizar en una misma vista 
        """
        for self_id in self:
            self_id.partner_name = self_id.order_id.partner_id.name
            self_id.folio_invoice = self_id.account_id.number
            self_id.Category_pdt = self_id.product_id.categ_id.name
            self_id.currency = self_id.order_id.currency_id.name
            self_id.total_invoice = self_id.account_id.amount_total
            self_id.depto_name = self_id.order_id.requisition_id.sudo().empl_department_id.name


    def _get_data_order(self):
        for rec in self:
            if rec.purchase_line_id:
                rec.account_analytic_id = rec.purchase_line_id.account_analytic_id.id
                rec.udm_pdt = rec.purchase_line_id.product_uom.name
            elif rec.product_id and rec.order_id:
                purchase_line = rec.env['purchase.order.line'].search([
                    ('order_id', '=', rec.order_id.id), ('product_id', '=', rec.product_id.id)], limit=1)
                if purchase_line:
                    rec.account_analytic_id = purchase_line.account_analytic_id.id
                    rec.udm_pdt = purchase_line.product_uom.name
            if rec.product_id and rec.account_id:
                if rec.account_id.state != 'draft':
                    invoice_line = rec.env['account.invoice.line'].search([
                        ('invoice_id', '=', rec.account_id.id), ('product_id', '=', rec.product_id.id)], limit=1)
                    if invoice_line:
                        rec.subtotal = invoice_line.price_subtotal
                        rec.tax = invoice_line.price_total - invoice_line.price_subtotal


    def _get_exchangerate(self):
        for rec in self:
            if rec.order_id.currency_id.name != 'MXN':
                rate = rec.env['res.currency.rate'].search([('currency_id', '=', rec.order_id.currency_id.id), ('name', '<=', rec.date_request)], limit=1)
                if rate:
                    rec.c_exchangerate = rate.rate


    name = fields.Char(
        string='Referencia',
    )
    product_id = fields.Many2one(
        'product.product',
        string='Producto',
        track_visibility='onchenge'
    )    
    order_id = fields.Many2one(
        'purchase.order',
        string='Documento asociado',
        track_visibility='onchenge'
    )
    move_line = fields.Many2one(
        'stock.move.line',
        string='Movimiento',
        track_visibility='onchenge'
    )
    qty = fields.Float(digits=dp.get_precision('Entradas'),
        string='Cantidad esperada',
        track_visibility='onchenge',
    )
  
    get_qty = fields.Float(digits=dp.get_precision('Entradas'),
        string='Cantidad recibida',
        track_visibility='onchenge'
    )
    coments = fields.Text(
        string='Comentarios',
        track_visibility='onchenge'
    )
    state = fields.Selection(
        selection=[
                    ('create', 'Creado'),
                    ('received', 'Recibido'),
                    ('cancel', 'Cancelado'),
                ],
                default='create',
        help="",
        track_visibility='onchenge'
    )
    date_request = fields.Date(
        string='Fecha de entrada',
        track_visibility='onchenge'
    )
    doc = fields.Char(
        string='Documento',
    )
    account_id = fields.Many2one(
        'account.invoice',
        string='Factura asociada',
        track_visibility='onchenge'
    )

    partner_name = fields.Char(
        string='Proveedor',
        compute=get_name_resum)

    folio_invoice = fields.Char(
        string='Folio factura',
        compute=get_name_resum)

    depto_name = fields.Char(
        string='Departamento solicitante',
        compute=get_name_resum) 

    Category_pdt = fields.Char(
        string='Categoria del producto',
        compute=get_name_resum) 

    udm_pdt = fields.Char(
        string='Unidad de medida',
        compute=_get_data_order)

    currency = fields.Char(
        string='Moneda',
        compute=get_name_resum)

    total_invoice  = fields.Float(
        string='Total factura',
        compute=get_name_resum)

    company_id = fields.Many2one(
        'res.company',
        string='Compañía',
        track_visibility='onchenge')

    picking_id = fields.Many2one(
        'stock.picking',
        string='Picking'
    )

    purchase_line_id = fields.Many2one(
        'purchase.order.line',
        string='Descripción',
        domain="[('order_id', '=', order_id), ('product_id', '=', product_id)]"
    )

    account_analytic_id = fields.Many2one(
        'account.analytic.account',
        string='Cuenta analitica',
        compute=_get_data_order
    )

    subtotal = fields.Float(
        string='Subtotal',
        compute = _get_data_order
    )

    tax = fields.Float(
        string='Total impuestos',
        compute=_get_data_order
    )

    c_exchangerate = fields.Float(
        string='Tipo de cambio al dia de la orden de compra',
        compute=_get_exchangerate
    )

    exchangerate = fields.Float(
        string='Tipo de cambio'
    )

    destination = fields.Many2one(
        'stock.location',
        String='Almacen de destino'
    )

    rep_employee = fields.Many2one(
        'hr.employee',
        String="Empleado que recibe"
    )



    def force_unlink(self):
        """
        Forzar eliminación.
        """        
        return super(purchase_reception, self).unlink()



    def get_current_date(self):
        """
        Regresa la hora actual.
        """
        return date.today().strftime('%Y-%m-%d')


    def cancel(self):
        """
        Cambia de estado a cancelado 
        """
        self.state = 'cancel'


    def get_good(self):
        """
        Resta la cantidad residida y crea la parcialidad si es necesario y le agrega la fecha de entrada.
        """
        if self.get_qty < 0.00001:
            raise ValidationError('Se debe de recibir por lo menos 1 producto.')

        if self.get_qty > self.qty:
            raise ValidationError('No se puede recibir más de la cantidad esperada.')

        qty_total = float(self.qty) - float(self.get_qty)

        if self.qty > self.get_qty:

            self.env['purchase.reception'].create({'name':'Pendiente de recibir','product_id': self.product_id.id, 'order_id': self.order_id.id, 'qty': qty_total,'company_id':self.company_id.id})


        folio_sequence = self.env['ir.sequence'].sudo().search([('name', '=', 'reception'),('company_id', '=', self.company_id.id)], limit=1)
        self.name = folio_sequence._next()
        self.date_request = self.get_current_date()
        self.state = 'received'
    


    @api.model
    def create(self, vals):
        """
        Resta la cantidad residida y crea la parcialidad si es necesario y le agrega la fecha de entrada.
        """
        try: 
            if vals['state'] == 'received':
                folio_sequence = self.env['ir.sequence'].sudo().search([('name', '=', 'reception'),('company_id', '=', self.company_id.id)], limit=1)
                if not folio_sequence:
                    raise ValidationError('No está configurada una secuencia para la compañía .')
                vals['name'] = folio_sequence._next()
        except Exception:
            pass
        return super(purchase_reception, self).create(vals)

    @api.multi
    def unlink(self):
        """
        Restringe la eliminación de entradas.
        """
        raise ValidationError('No puedes eliminar una entrada solo cancelarla.')

    def init(self):
        self._cr.execute("""
        DROP TRIGGER IF EXISTS reception_trg ON purchase_reception;
        
        CREATE OR REPLACE FUNCTION public.reception_trg()
          RETURNS trigger AS
        $BODY$ DECLARE
                v_account_invoice_id INTEGER;
                VCAN INTEGER;
            BEGIN
            
            IF (TG_OP='UPDATE') THEN
        
                SELECT account_invoice_id INTO v_account_invoice_id FROM account_invoice_purchase_reception_rel WHERE purchase_reception_id = NEW.ID;
            
                IF NEW.ACCOUNT_ID IS NOT NULL THEN
                    IF v_account_invoice_id IS NULL THEN
                    INSERT INTO public.account_invoice_purchase_reception_rel(
                        account_invoice_id, purchase_reception_id)
                        VALUES (NEW.ACCOUNT_ID, NEW.ID);
                    UPDATE account_invoice SET with_receptions= 'Con entradas'
                    WHERE ID = NEW.ACCOUNT_ID;
                    raise notice 'entro al insert';
                    RETURN NEW;
                    ELSE
                    UPDATE account_invoice_purchase_reception_rel SET account_invoice_id = NEW.ACCOUNT_ID
                    WHERE purchase_reception_id = NEW.ID;
                    UPDATE account_invoice SET with_receptions= 'Con entradas'
                    WHERE ID = NEW.ACCOUNT_ID;
                    raise notice 'emtrp al else';
                    END IF;
                ELSE
                    IF v_account_invoice_id IS NOT NULL THEN
                    DELETE FROM account_invoice_purchase_reception_rel WHERE purchase_reception_id = NEW.ID;
                    END IF;
                END IF;
        
                SELECT COUNT(*) INTO VCAN FROM account_invoice_purchase_reception_rel WHERE account_invoice_id = v_account_invoice_id;
                raise notice '%',vcan;
                IF VCAN > 0 THEN
                    UPDATE account_invoice SET with_receptions= 'Con entradas'
                    WHERE ID = v_account_invoice_id;
                    raise notice 'con';
                ELSE
                    UPDATE account_invoice SET with_receptions= 'Sin entradas'
                    WHERE ID = v_account_invoice_id;
                    raise notice 'sin';
                END IF;
        
                RETURN NEW;
        
            ELSIF (TG_OP='DELETE') THEN
        
                 SELECT account_invoice_id INTO v_account_invoice_id FROM account_invoice_purchase_reception_rel WHERE purchase_reception_id = OLD.ID;	
        
                 DELETE FROM account_invoice_purchase_reception_rel WHERE purchase_reception_id = OLD.ID;
                 
                 SELECT COUNT(*) INTO VCAN FROM account_invoice_purchase_reception_rel WHERE account_invoice_id = v_account_invoice_id;
                raise notice '%',vcan;
                IF VCAN > 0 THEN
                    UPDATE account_invoice SET with_receptions= 'Con entradas'
                    WHERE ID = v_account_invoice_id;
                    raise notice 'con';
                ELSE
                    UPDATE account_invoice SET with_receptions= 'Sin entradas'
                    WHERE ID = v_account_invoice_id;
                    raise notice 'sin';
                END IF;
        
                RETURN OLD;
            
            END IF;
            END
        
                                ; $BODY$
          LANGUAGE plpgsql VOLATILE
          COST 100;
        ALTER FUNCTION public.reception_trg()
          OWNER TO odoo;

        CREATE TRIGGER reception_trg
          BEFORE UPDATE OR DELETE
          ON purchase_reception
          FOR EACH ROW
          EXECUTE PROCEDURE reception_trg();""")
