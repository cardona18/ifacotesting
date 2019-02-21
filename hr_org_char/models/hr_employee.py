# -*- coding: utf-8 -*-
# © <2017> <Juan Carlos VB (jcvazquez@gmail.com)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api

class hr_employee(models.Model):
    _inherit    = 'hr.employee'

    @api.multi
    def view_in_org_char(self):
    	for self_id in self:
    		url = '/web/org_char/'+str(self_id.id)

    		return {
                  'name'     : 'Ir a organigrama',
                  'res_model': 'ir.actions.act_url',
                  'type'     : 'ir.actions.act_url',
                  'target'   : '_blank',
                  'url'      :  url
             }
