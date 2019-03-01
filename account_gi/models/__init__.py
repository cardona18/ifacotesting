# -*- coding: utf-8 -*-
from . import account_invoice
# from . import account_partner_ledger
# from . import report_account_report_trialbalance
from . import res_partner
from . import account_payment
from . import account_move
from . import res_reasons_types
from . import res_cancel_types

#Migracion

#Borrado en el .csv
#hr_expense.access_uom_uom_hr_expense_user,product.uom.hr.expense.user,product.model_uom_uom,hr_expense.group_hr_expense_user,1,0,0,0
#mrp.access_uom_uom_mrp_manager,product.uom mrp_manager,product.model_uom_uom,mrp.group_mrp_manager,1,0,0,0
#sale.access_uom_uom_sale_manager,product.uom salemanager,product.model_uom_uom,sales_team.group_sale_manager,1,0,0,0
#purchase.access_uom_uom_purchase_manager,product.uom purchase_manager,product.model_uom_uom,purchase.group_purchase_manager,1,0,0,0
#stock.access_uom_uom_stock_manager,product.uom stock_manager,product.model_uom_uom,stock.group_stock_manager,1,0,0,0
#,,,,,,,