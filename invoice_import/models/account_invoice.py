# -*- coding: utf-8 -*-
# © <2016> <Omar Torres Silva (otorres@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from dateutil import parser
from pytz import timezone
import base64
import decimal
import logging
import os.path
import subprocess
from urllib.parse import quote

from odoo import fields, models, api
from odoo.exceptions import UserError
from odoo.addons.mssql_proxy.utils.proxy_manager import Manager

from .num2words import Numero_a_Texto

_logger = logging.getLogger(__name__)

context = decimal.getcontext()
context.rounding = decimal.ROUND_HALF_UP

class account_invoice_gi(models.Model):
    _inherit = 'account.invoice'

    siagi_state = fields.Selection(
        string='Estado SIAGI',
        default='NS',
        size=2,
        selection=[
            ('NS', 'Pendiente'),
            ('SY', 'Timbrada'),
            ('CA', 'Cancelada'),
            ('ER', 'Error')
        ]
    )
    order_num = fields.Char(
        string='Número de pedido',
        size=40
    )
    siagi_origin_inv = fields.Char(
        string='Factura origen',
        size=60
    )

    employee_assig_inv = fields.Char(
        string='Personal de compras asignado en la OC',
        compute='_get_employee_assig'
    )

    def _get_employee_assig(self):
        for self_id in self:
            name_oc = self.env['purchase.order'].search([('name', '=', self_id.origin)], limit=1)
            nameint = int(name_oc.employee_assig)
            name_oc_id = self.env['hr.employee'].search([('id', '=', nameint)], limit=1)
            print(name_oc)
            print(name_oc.employee_assig)
            print(nameint)
            print(name_oc_id)
            print(name_oc_id.work_email)
            name_f = name_oc_id.work_email
            self.employee_assig_inv = name_f
            return name_f

    current_user = fields.Many2one(
        'res.users',
        'Current User',
        default=lambda self: self.env.user)

    def execute(self, _command):
        try:
            return subprocess.check_output(_command, shell=True, stderr=subprocess.STDOUT)
        except Exception as e:
            _logger.error('EXECUTE ERROR: %s', e)

    @api.multi
    def l10n_mx_edi_amount_to_text(self):

        self.ensure_one()

        return Numero_a_Texto(self.amount_total)

    def report_format_address(self, atype='C'):

        if atype == 'C':
            return self._format_partner_address(self.partner_id)

        if atype == 'S':
            return self._format_partner_address(self.partner_shipping_id)

    def _format_partner_address(self, partner_id):

        return '%s%s%s%s%s%s%s%s%s' % (
            '%s ' % partner_id.street_name if partner_id.street_name else '',
            '%s ' % partner_id.street_number if partner_id.street_number else '',
            '%s ' % partner_id.street_number2 if partner_id.street_number2 else '',
            '%s ' % partner_id.l10n_mx_edi_colony if partner_id.l10n_mx_edi_colony else '',
            '%s ' % partner_id.l10n_mx_edi_locality if partner_id.l10n_mx_edi_locality else '',
            'CP: %s ' % partner_id.zip if partner_id.zip else '',
            '%s ' % partner_id.city if partner_id.city else '',
            '%s ' % partner_id.state_id.name if partner_id.state_id.name else '',
            partner_id.country_id.name
        )

    def _get_sat_cadena(self, tfd):

        self.ensure_one()

        return '||%s|%s|%s|%s%s|%s|%s||' % (
            tfd.get('Version'),
            tfd.get('UUID'),
            tfd.get('FechaTimbrado'),
            tfd.get('RfcProvCertif'),
            '|%s' % tfd.get('Leyenda') if tfd.get('Leyenda') else '',
            tfd.get('SelloCFD'),
            tfd.get('NoCertificadoSAT')
        )

    @api.multi
    def action_invoice_open(self):

        result = super(account_invoice_gi, self).action_invoice_open()

        if self.l10n_mx_edi_pac_status == 'signed':
            self.update_siagi_signed()
        else:
            self.siagi_state = 'ER'

        return result

    @api.multi
    def action_invoice_cancel_gi(self):

        result = super(account_invoice_gi, self).action_invoice_cancel()
        if self.l10n_mx_edi_pac_status == 'cancelled' and self.siagi_state == 'SY':
            self.update_siagi_cancelled()
        else:
            self.siagi_state = 'ER'

        return result

    @api.multi
    def retry_siagi_state(self):

        if self.l10n_mx_edi_pac_status == 'signed':
            self.update_siagi_signed()

        if self.l10n_mx_edi_pac_status == 'cancelled':
            self.update_siagi_cancelled()

    def update_siagi_signed(self):

        self.ensure_one()

        if not self.origin:
            return False

        if self.origin[:5] != 'SIAGI':
            return False

        # PARSE XML
        cfdi = self.l10n_mx_edi_get_xml_etree()
        tfd  = cfdi.find('.//{http://www.sat.gob.mx/TimbreFiscalDigital}TimbreFiscalDigital')

        # COMPANY RFC
        company_rfc = str(self.execute('php /opt/php_files/invoice_query.php RFC %s' % self.company_id.invoice_db).decode('UTF-8'))

        if not company_rfc:
            raise UserError('RFC no encontrado para: %s' % self.company_id.invoice_db)

        # PARSE DATES
        outformat = '%d/%m/%Y %H:%M:%S'
        send_date = parser.parse(cfdi.get('Fecha'))
        sign_date = parser.parse(tfd.get('FechaTimbrado'))

        siagi_sqlres = Manager.app_command({
            'db_user': self.company_id.sudo().import_server_id.server_user,
            'db_host': self.company_id.sudo().import_server_id.server_addr,
            'db_pass': self.company_id.sudo().import_server_id.server_pass,
            'db': self.company_id.invoice_db,
            'sql': base64.b64encode(bytes("""EXEC ActualizarCFDI @RfcCia = {rfc}, @TipDoc = '{doc_type}', @Tipo = '{invoice_type}', @FecHor = '{date_time}', @FecRptSat = '{sign_date}', @XML_UUID = '{uuid}', @XMLFile = '{xml}', @NumDocInt = '{invoice_num}'""".strip().format(
                rfc=company_rfc,
                invoice_num=self.origin[6:],
                doc_type='FAC' if self.type == 'out_invoice' else 'NCR',
                date_time=send_date.strftime(outformat),
                sign_date=sign_date.strftime(outformat),
                invoice_type='I' if self.type == 'out_invoice' else 'E',
                uuid=tfd.get('UUID'),
                xml=base64.b64decode(self.l10n_mx_edi_cfdi).decode('UTF-8')
            ), "utf-8")).decode("utf-8")
        }, True).decode("utf-8")

        siagi_cifsres = Manager.app_command({
            'smb_domain': self.company_id.sudo().smb_domain,
            'smb_user': self.company_id.sudo().smb_user,
            'smb_pass': self.company_id.sudo().smb_pass,
            'smb_path': '%s/%s' % (self.company_id.sudo().smb_path, 'Cfdi%s_%s.xml' % (
                send_date.strftime('%Y%m%d'),
                self.origin[6:]
            )),
            'xml': self.l10n_mx_edi_cfdi.decode("utf-8")
        }, True, 'CIFSProxy').decode("utf-8")

        if siagi_sqlres != '1':
            _logger.error("SIAGI SQL ERROR: %s", siagi_sqlres)
            self.siagi_state = 'ER'
            return False

        if siagi_cifsres != '1':
            _logger.error("SIAGI CIFS ERROR: %s", siagi_cifsres)
            self.siagi_state = 'ER'
            return False

        self.siagi_state = 'SY'
        return True


    def update_siagi_cancelled(self):

        self.ensure_one()

        try:

            cfdi_id = int(self.execute('php /opt/php_files/invoice_query.php %s %s %s' % (
                'UPD' if self.type == 'out_invoice' else 'UPDN',
                self.company_id.invoice_db,
                self.origin[6:]
            )))

            update_sql = ''

            if self.type == 'out_invoice':
                update_sql = "UPDATE FactVtas SET fvt_IdCfd = IDENT_CURRENT('CfdSat') WHERE Fvt_Numero = %s" % self.origin[6:]
            else:
                update_sql = "UPDATE NCredito SET Ncr_IdCfd = IDENT_CURRENT('CfdSat') WHERE Ncr_Numero = %s" % self.origin[6:]

            siagi_sqlres = Manager.app_command({
                'db_user': self.company_id.sudo().import_server_id.server_user,
                'db_host': self.company_id.sudo().import_server_id.server_addr,
                'db_pass': self.company_id.sudo().import_server_id.server_pass,
                'db': self.company_id.invoice_db,
                'sql': base64.b64encode(bytes("""
                    INSERT INTO CfdSat
                        (Cfd_AnoFol, Cfd_Numfol, Cfd_TipDoc, Cfd_NumCer, Cfd_Tipo, Cfd_Estatus, Cfd_FecHor,
                        Cfd_FecRptSat, Cfd_IdPoliza, Cfd_TipoPoliza, Cfd_NumPoliza, Cfd_NumAprFol, Cfd_NumDocInt,
                        Cfd_FechaCreado, Cfd_ClvUsuario, Cfd_ImpIva, Cfd_ImpDscto, Cfd_ImpTotal, Cfd_ClaveCli, Cfd_UUID)
                    SELECT
                        Cfd_AnoFol, Cfd_Numfol, Cfd_TipDoc, Cfd_NumCer, Cfd_Tipo, 'C', GETDATE(),
                        Cfd_FecRptSat, 0, 0, 0, Cfd_NumAprFol, Cfd_NumDocInt, GETDATE(), Cfd_ClvUsuario,
                        Cfd_ImpIva*-1, Cfd_ImpDscto*-1, Cfd_ImpTotal*-1, Cfd_ClaveCli, Cfd_UUID
                    FROM
                        CfdSat
                    WHERE
                        cfd_idfolio = {cfdi_id};

                    {update_sql}
                """.strip().format(cfdi_id=cfdi_id, update_sql=update_sql), "utf-8")).decode("utf-8")
            }, True).decode("utf-8")

            if siagi_sqlres != '1':
                _logger.error("SIAGI SQL ERROR: %s", siagi_sqlres)
                self.siagi_state = 'ER'
                return False

            new_cfdi_id = int(self.execute('php /opt/php_files/invoice_query.php %s %s %s' % (
                'UPD' if self.type == 'out_invoice' else 'UPDN',
                self.company_id.invoice_db,
                self.origin[6:]
            )))

        except Exception as e:
            _logger.debug("CANCEL ERROR: %s", e)
            return False

        if new_cfdi_id > cfdi_id:
            self.siagi_state = 'CA'
            return True

        return False

    @api.multi
    def _l10n_mx_edi_create_cfdi_values(self):

        precision_digits = self.env['decimal.precision'].precision_get('Account')
        res = super(account_invoice_gi, self)._l10n_mx_edi_create_cfdi_values()
        invoice_lines = self.invoice_line_ids
        res['amount_untaxed'] =  invoice_lines.monetary_round(
            sum( l.invoice_line_amount(l.quantity, l.price_unit) for l in invoice_lines ), 2
        )

        return res

    def check_lines_shipment(self):

        self.ensure_one()

        for line in self.invoice_line_ids:

            if line.shipment_num:
                return True

        return False

    def check_lines_predial(self):

        self.ensure_one()

        for line in self.invoice_line_ids:

            if line.predial_account:
                return True

        return False

    def check_lines_sat_code(self):

        self.ensure_one()

        for line in self.invoice_line_ids:

            if line.product_id.l10n_mx_edi_code_sat_id.code:
                return True

        return False

    def check_lines_cbss(self):

        self.ensure_one()

        for line in self.invoice_line_ids:

            if line.product_cbss:
                return True

        return False

    @api.multi
    @api.depends('l10n_mx_edi_cfdi_name')
    def _compute_cfdi_values(self):
        '''Fill the invoice fields from the cfdi values.
        '''
        for inv in self:
            attachment_id = inv.l10n_mx_edi_retrieve_last_attachment()
            if not attachment_id:
                continue
            # At this moment, the attachment contains the file size in its 'datas' field because
            # to save some memory, the attachment will store its data on the physical disk.
            # To avoid this problem, we read the 'datas' directly on the disk.
            datas = attachment_id._file_read(attachment_id.store_fname)
            inv.l10n_mx_edi_cfdi = datas
            tree = inv.l10n_mx_edi_get_xml_etree(base64.decodestring(datas))
            # if already signed, extract uuid
            tfd_node = inv.l10n_mx_edi_get_tfd_etree(tree)
            if tfd_node is not None:
                inv.l10n_mx_edi_cfdi_uuid = tfd_node.get('UUID')
            inv.l10n_mx_edi_cfdi_amount = tree.get('Total')
            inv.l10n_mx_edi_cfdi_supplier_rfc = tree.Emisor.get('Rfc')
            inv.l10n_mx_edi_cfdi_customer_rfc = tree.Receptor.get('Rfc')
            certificate = tree.get('noCertificado', tree.get('NoCertificado'))
            inv.l10n_mx_edi_cfdi_certificate_id = self.env['l10n_mx_edi.certificate'].sudo().search(
                [('serial_number', '=', certificate)], limit=1)

    @api.multi
    def search_siagi_origin_inv(self):
        '''Search related refund invoice.
        '''

        self.ensure_one()

        inv = self.search([
            ('type', '=', 'out_invoice'),
            ('origin', '=', self.siagi_origin_inv),
            ('company_id', '=', self.company_id.id)
        ], limit=1)

        if inv.l10n_mx_edi_cfdi_uuid:
            self.refund_invoice_id = inv.id
            self.l10n_mx_edi_origin = '01|%s' % inv.l10n_mx_edi_cfdi_uuid