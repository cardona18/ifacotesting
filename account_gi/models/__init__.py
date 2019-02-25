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
#,,,,,,,
#stock.access_product_uom_categ_stock_manager,product.uom.categ stock_manager,product.model_product_uom_categ,stock.group_stock_manager,1,1,0,0
#purchase.access_product_uom_categ_purchase_manager,product.uom.categ purchase_manager,product.model_product_uom_categ,purchase.group_purchase_manager,1,1,0,0
#sale.access_product_uom_categ_sale_manager,product.uom.categ salemanager,product.model_product_uom_categ,sales_team.group_sale_manager,1,1,0,0
#mrp.access_product_uom_categ_mrp_manager,product.uom.categ mrp_manager,product.model_product_uom_categ,mrp.group_mrp_manager,1,1,0,0