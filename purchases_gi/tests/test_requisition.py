import logging
from odoo.tests import common
_logger = logging.getLogger(__name__)

class TestRequisition(common.TransactionCase):

    def setUp(self):
        super(TestRequisition, self).setUp()
        self.employee = self.env['hr.employee']
        self.product = self.env['product.product'].search([('purchase_ok', '=', True)],limit=1)
        self.account_analytic = self.env['account.analytic.account']


    def test_requisition_create(self):
        company_id = self.env['res.company'].search([('id', '=', 5)], limit=1)

        #emplyee_id = self.env['hr.employee'].search([('id', '=', 1042)]) #ID ADMIN

        folio_sequence = self.env['ir.sequence'].sudo().search(
            [('name', '=', 'purchase_requisition'), ('company_id', '=', company_id.id)], limit=1)

        print("Creando encabezado de solicitud de compra....")

        req = self.env['purchase.requisition'].create({
            'name': folio_sequence._next(),
            'employee_purchase_reque': self.employee.id,
            'employee_approve': self.employee.id,
            'employee_authorize': self.employee.id,
            'company_id': company_id.id,

        })

        print("Creando 1 linea para la solicitud de compra....")

        #product_id = self.env['product.product'].search([('purchase_ok', '=', True)],limit=1)

        req_line = self.env['purchase.requisition.line'].create({
            'product_id': self.product.id,
            'description_product': self.product.name,
            'product_qty': 1,
            'product_uom_id': self.product.uom_id.id,
            'account_analytic_id': self.account_analytic.id,
            'requisition_id': req.id
        })

        req.write({'line_ids': req_line})

        print("Solicitud en estado borrador")
        self.assertEqual(req.state, 'draft')

        print("Solicitud enviada")
        req.send_request_purchanse()
        self.assertEqual(req.state, 'send')

        print("Solicitud aprobada")
        req.request_purchanse_approve()
        self.assertEqual(req.state, 'approve')

        print("Solicitud enviar a autorizar")
        req.analyze_quotes()
        self.assertEqual(req.state, 'in_progress')
