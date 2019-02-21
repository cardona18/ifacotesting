# -*- coding: utf-8 -*-
# © <2017> <Juan Carlos Vazquez Beas (jcvazquez@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from datetime import datetime, date, timedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT

import sys, logging
from openerp.osv import osv
from odoo import fields, models, api

_logger = logging.getLogger(__name__)

class import_licenses(models.Model):
    """
    Se creó el modelo permiso de importación ya que es necesario en el módulo de compras.
    """
    _name = 'import.licenses'
    _inherit = ['mail.thread']

    _sql_constraints = [
      ('name', 'unique(name)', 'Ya existe un permiso de importación con ese número de autorización')
    ]

    def chek_status(self):
        """
        Verifica si no ha caducado un permiso de importación depende de la fecha cambia su estado.
        """
        if self.end_to_extend:
            if str(date.today()) > self.end_to_extend:
                self.state = 'losing'
            else:
                self.state = 'valid'

        else:
            if str(date.today()) > self.end_validity:
                self.state = 'losing'
            else:
                self.state = 'valid'


    def get_product_to_use(self):
        """
        Busca productos relacionados con la orden de compra
        """
        product = self.env['product.template'].sudo().search([('import_license','=',self.id)])
        if product:
            query = """
                    UPDATE import_licenses SET is_linked = True WHERE id = %s;
                    """
            self.env.cr.execute(query % (self.id))
        else:
            query = """
                    UPDATE import_licenses SET is_linked = False WHERE id = %s;
                    """
            self.env.cr.execute(query % (self.id))

        self.product_id = product


    name_product = fields.Char(
        string='Nombre del producto',
        required=True
    )

    name_and_license = fields.Char(
        string='Nombre del producto / licencia ',
        required=True,
        default="En borrador"
    )

    name = fields.Char(
        string='Número de autorización',
        required=True,
    )

    is_linked = fields.Boolean(
        string='Esta vinculado',
    )

    validity = fields.Date(
        string='Vigencia',
        required=True,
        default=date.today(),
    )

    end_validity = fields.Date(
        string='Hasta',
        required=True,
        default=date.today(),
    )

    to_extend = fields.Date(
        string='Extender',
    )

    end_to_extend = fields.Date(
        string='Hasta',
    )

    import_license_file = fields.Binary(
        string='Permiso de importación',
        required=True,
    )

    import_license_filename = fields.Char(
        string='Nombre del archivo',
    )

    quantity = fields.Integer(
        string='Cantidad',
        required=True,
    )

    uom_license = fields.Many2one(
        string='Unidad de medida',
        comodel_name='product.uom',
        required=True,
    )

    tariff_fraction = fields.Char(
        string='Fracción arancelaria',
        required=True,
    )

    report_expiration = fields.Integer(
        string='Notificar antes de vencimiento',
        help="Mandar alerta antes de que el permiso expire, (cantidad en días)."
    )

    state = fields.Selection(
        [('valid', 'Valido'),
        ('losing', 'Vencido')], 
        string='Estado', 
        default='valid',
        compute=chek_status
    )

    product_id = fields.Many2one(
        string='Producto',
        comodel_name='product.template',
        compute=get_product_to_use
    )


    @api.multi
    def unlink(self):
        """
        Bloque eliminar permisos de importación.
        """
        raise osv.except_osv('Advertencia','No puedes eliminar un permiso de importación.')


    @api.multi
    def write(self,vals):
        """
        Crea un historial de las fechas al cambiarse.
        """
        res = super(import_licenses, self).write(vals)

        try:
            if vals['end_validity']:
                self.sudo().message_post('Sé a modificado la vigencia hasta '+vals['end_validity']+' por el empleado '+ str(self.env.user.employee_ids.name))
        except KeyError:
            pass    

        try:
            if vals['end_to_extend']:
                self.sudo().message_post('Sé a extendido hasta '+vals['end_to_extend']+' por el empleado '+ str(self.env.user.employee_ids.name))
        except KeyError:
            pass 
        return res


    @api.model
    def create(self, vals):
        """
        Verifica que la licencia sea para más de 0 productos.
        """
        if vals['quantity'] <= 0:
            raise osv.except_osv('Advertencia','No se puede crear un permiso de importación con una cantidad en cero.')

        vals['name_and_license'] = str(vals['name_product'])+' / '+str(vals['name'])
        new_id = super(import_licenses, self).create(vals)
        return new_id


    @api.model
    def hr_import_licenses_cron(self):
        """
        Esta función notifica cuando un permiso de importación está próximo a caducar y cuando vence.
        """
        licenses_ids = self.env['import.licenses'].sudo().search([('state','=','validity')])

        for license_id in licenses_ids:
            if license_id.report_expiration > 0:

                to_date = datetime.strptime(license_id.end_validity, DEFAULT_SERVER_DATE_FORMAT) if type(license_id.end_validity) is str else license_id.end_validity
                to_date = to_date  - timedelta(days=license_id.report_expiration)

                get_today = date.today()
                

                if str(get_today)  == str(to_date)[0:10]:


                    date_formated = license_id.end_validity.split("-")
                    date_form = str(date_formated[2]+'-'+date_formated[1]+'-'+date_formated[0])

                    manssage_body = '''
                                        <h3>
                                            El permiso de importación esta próximo a vencer para el producto llamado '''+license_id.name_product+''' con el numero de autorización '''+license_id.name+'''
                                            Esta próximo a vencer <br/>
                                        </h3>
                                        <h1>
                                            El producto vencerá el '''+date_form+'''
                                        </h1>
                                        <h3>
                                            Fue creado por el usuario '''+license_id.create_uid.name+'''.
                                        </h3>
                                    '''

                    post_vars = {'subject': "Permiso de importación vencido", 'body': manssage_body,}
                    license_id.sudo().message_post(type="notification", subtype="mt_comment", **post_vars)
