# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import base64
import logging
import sys  
from odoo import http, _
from odoo import api, http, registry, SUPERUSER_ID, _
from odoo.addons.website.models.website import slug
from odoo.exceptions import AccessError
from odoo.http import request

reload(sys)  
sys.setdefaultencoding('utf8')

_logger = logging.getLogger(__name__)

class WebsiteHrRecruitment_gi(http.Controller):

    @http.route([
        '/jobs',
        '/jobs/country/<model("res.country"):country>',
        '/jobs/department/<model("hr.department"):department>',
        '/jobs/country/<model("res.country"):country>/department/<model("hr.department"):department>',
        '/jobs/office/<int:office_id>',
        '/jobs/country/<model("res.country"):country>/office/<int:office_id>',
        '/jobs/department/<model("hr.department"):department>/office/<int:office_id>',
        '/jobs/country/<model("res.country"):country>/department/<model("hr.department"):department>/office/<int:office_id>',
    ], type='http', auth="public", website=True)
    def jobs(self, country=None, department=None, office_id=None, **kwargs):
        env = request.env(context=dict(request.env.context, show_address=True, no_tag_br=True))

        Country = env['res.country']
        Jobs = env['hr.job']

        # List jobs available to current UID
        job_ids = Jobs.search([], order="website_published desc,no_of_recruitment desc").ids
        # Browse jobs as superuser, because address is restricted
        jobs = Jobs.sudo().browse(job_ids)

        # Default search by user country
        if not (country or department or office_id or kwargs.get('all_countries')):
            country_code = request.session['geoip'].get('country_code')
            if country_code:
                countries_ = Country.search([('code', '=', country_code)])
                country = countries_[0] if countries_ else None
                if not any(j for j in jobs if j.address_id and j.address_id.country_id == country):
                    country = False

        # Filter job / office for country
        if country and not kwargs.get('all_countries'):
            jobs = [j for j in jobs if j.address_id is None or j.address_id.country_id and j.address_id.country_id.id == country.id]
            offices = set(j.address_id for j in jobs if j.address_id is None or j.address_id.country_id and j.address_id.country_id.id == country.id)
        else:
            offices = set(j.address_id for j in jobs if j.address_id)

        # Deduce departments and countries offices of those jobs
        departments = set(j.department_id for j in jobs if j.department_id)
        countries = set(o.country_id for o in offices if o.country_id)

        if department:
            jobs = (j for j in jobs if j.department_id and j.department_id.id == department.id)
        if office_id and office_id in map(lambda x: x.id, offices):
            jobs = (j for j in jobs if j.address_id and j.address_id.id == office_id)
        else:
            office_id = False


        units_ids = Jobs.sudo().search([('category_job','=','is_director')], order="id asc")
        _logger.warning("----------------")
        _logger.warning(units_ids)

        # Render page
        return request.render("website_hr_recruitment_gi.index", {
            'jobs': jobs,
            'countries': countries,
            'departments': departments,
            'offices': offices,
            'country_id': country,
            'department_id': department,
            'office_id': office_id,
            'units':units_ids,
        })

    @http.route('/jobs/add', type='http', auth="user", website=True)
    def jobs_add(self, **kwargs):
        job = request.env['hr.job'].create({
            'name': _('Job Title'),
        })
        return request.redirect("/jobs/detail/%s?enable_editor=1" % slug(job))

    @http.route('/jobs/detail/<model("hr.job"):job>', type='http', auth="public", website=True)
    def jobs_detail(self, job, **kwargs):
        return request.render("website_hr_recruitment_gi.detail", {
            'job': job,
            'main_object': job,
        })

    @http.route('/jobs/apply/<model("hr.job"):job>', type='http', auth="public", website=True)
    def jobs_apply(self, job, **kwargs):
        error = {}
        default = {}
        if 'website_hr_recruitment_gi_error' in request.session:
            error = request.session.pop('website_hr_recruitment_gi_error')
            default = request.session.pop('website_hr_recruitment_gi_default')
        return request.render("website_hr_recruitment_gi.apply", {
            'job': job,
            'error': error,
            'default': default,
        })

    def _get_applicant_char_fields(self):
        return ['email_from', 'partner_name', 'description']

    def _get_applicant_relational_fields(self):
        return ['department_id', 'job_id']

    def _get_applicant_files_fields(self):
        return ['ufile']

    def _get_applicant_required_fields(self):
        return ["partner_name", "phone", "email_from"]

    def _get_applicant_gi_data(self):
        return ["last_level_edu"]


    @http.route('/jobs/thankyou', methods=['POST'], type='http', auth="public", website=True, csrf=False)
    def jobs_thankyou(self, **post):
        error = {}
       
        for field_name in self._get_applicant_required_fields():
            if not post.get(field_name):
                error[field_name] = 'missing'
        if error:
            request.session['website_hr_recruitment_gi_error'] = error
            for field_name in self._get_applicant_files_fields():
                f = field_name in post and post.pop(field_name)
                if f:
                    error[field_name] = 'reset'
            request.session['website_hr_recruitment_gi_default'] = post
            return request.redirect('/jobs/apply/%s' % post.get("job_id"))

        env = request.env(user=SUPERUSER_ID)

        value = {
            # 'source_id' : env.ref('hr_recruitment_gi.source_website_company').id,
            'name': '    %s    \'Aplicación desde sitio web\'' % post.get('partner_name'), 
        }
        for f in self._get_applicant_char_fields():
            value[f] = post.get(f)
        for f in self._get_applicant_relational_fields():
            value[f] = int(post.get(f) or 0)

        value['partner_mobile'] = post.pop('phone', False)

        applicant_id = env['hr.applicant'].create(value).id


        for gi_data in self._get_applicant_gi_data():
            _logger.debug(gi_data)

        for field_name in self._get_applicant_files_fields():
            if post[field_name]:
                attachment_value = {
                    'name': post[field_name].filename,
                    'res_name': value['partner_name'],
                    'res_model': 'hr.applicant',
                    'res_id': applicant_id,
                    'datas': base64.encodestring(post[field_name].read()),
                    'datas_fname': post[field_name].filename,
                }
                env['ir.attachment'].create(attachment_value)


        applicant = http.request.env['hr.applicant'].sudo().search([('id','=',applicant_id)])
        applicant.sudo().address = post['address']

        applicant.sudo().env_job = post['env_job']
        applicant.sudo().home_job = post['home_job']
        applicant.sudo().code_job = post['code_job']
        applicant.sudo().flexi_job = post['flexi_job']
        applicant.sudo().facilities_job = post['facilities_job']
        applicant.sudo().feedback_job = post['feedback_job']
        applicant.sudo().benefits_job = post['benefits_job']
        applicant.sudo().salary_job = post['salary_job']
        applicant.sudo().technology_job = post['technology_job']
        applicant.sudo().social_job = post['social_job']


        
        return request.render("website_hr_recruitment_gi.thankyou", {})