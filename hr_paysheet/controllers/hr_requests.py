# -*- coding: utf-8 -*-

import os
import urllib

from openerp import http
from openerp.http import request
from openerp.addons.web.controllers.main import serialize_exception,content_disposition

class HRLeaveRequestManager(http.Controller):

    @http.route('/hr_request/holidays/accept', type='http')
    @serialize_exception
    def holidays_accept_action(self, **kw):
        """ Accept holidas request.
        @returns: :class:`werkzeug.wrappers.Response`
        """

        request_id = http.request.env['hr.holidays.request'].sudo().browse(int(kw['id']))

        if request_id.sudo().access_token != kw['token']:
            return http.request.render('hr_paysheet.message_template', {
                'message': 'Error de suplantación',
                'type': 'error'
            })

        if request_id.sudo().state in ('OK','REJ'):
            return http.request.render('hr_paysheet.message_template', {
                'message': 'La solicitud ya ha sido procesada',
                'type': 'error'
            })

        request_id.action_check('OK')

        return http.request.render('hr_paysheet.message_template', {
            'message': 'Solicitud aprobada con éxito',
            'type': 'ok'
        })

    @http.route('/hr_request/holidays/decline', type='http')
    @serialize_exception
    def holidays_decline_action(self, **kw):
        """ Decline holidas request.
        @returns: :class:`werkzeug.wrappers.Response`
        """

        request_id = http.request.env['hr.holidays.request'].sudo().browse(int(kw['id']))

        if request_id.sudo().access_token != kw['token']:
            return http.request.render('hr_paysheet.message_template', {
                'message': 'Error de suplantación',
                'type': 'error'
            })

        if request_id.sudo().state in ('OK','REJ'):
            return http.request.render('hr_paysheet.message_template', {
                'message': 'La solicitud ya ha sido procesada',
                'type': 'error'
            })

        request_id.action_check('REJ')

        return http.request.render('hr_paysheet.message_template', {
            'message': 'Solicitud declinada con éxito',
            'type': 'ok'
        })

    @http.route('/hr_request/leave/accept', type='http')
    @serialize_exception
    def leave_accept_action(self, **kw):
        """ Accept holidas request.
        @returns: :class:`werkzeug.wrappers.Response`
        """

        request_id = http.request.env['hr.leave.request'].sudo().browse(int(kw['id']))

        if request_id.sudo().access_token != kw['token']:
            return http.request.render('hr_paysheet.message_template', {
                'message': 'Error de suplantación',
                'type': 'error'
            })

        if request_id.sudo().state in ('OK','REJ'):
            return http.request.render('hr_paysheet.message_template', {
                'message': 'La solicitud ya ha sido procesada',
                'type': 'error'
            })

        request_id.action_check('OK')

        return http.request.render('hr_paysheet.message_template', {
            'message': 'Solicitud aprobada con éxito',
            'type': 'ok'
        })

    @http.route('/hr_request/leave/decline', type='http')
    @serialize_exception
    def leave_decline_action(self, **kw):
        """ Decline holidas request.
        @returns: :class:`werkzeug.wrappers.Response`
        """

        request_id = http.request.env['hr.leave.request'].sudo().browse(int(kw['id']))

        if request_id.sudo().access_token != kw['token']:
            return http.request.render('hr_paysheet.message_template', {
                'message': 'Error de suplantación',
                'type': 'error'
            })

        if request_id.sudo().state in ('OK','REJ'):
            return http.request.render('hr_paysheet.message_template', {
                'message': 'La solicitud ya ha sido procesada',
                'type': 'error'
            })

        request_id.action_check('REJ')

        return http.request.render('hr_paysheet.message_template', {
            'message': 'Solicitud declinada con éxito',
            'type': 'ok'
        })