
from odoo.addons.web_enterprise.models import ir_http

class HttpDev(ir_http.Http):

    def session_info(self):

        result = super(HttpDev, self).session_info()
        result['warning'] = False
        result['expiration_date'] = False
        result['expiration_reason'] = False

        return result