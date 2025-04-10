# -*- coding: utf-8 -*-
# from odoo import http


# class MedicalAppointmentSystem(http.Controller):
#     @http.route('/medical_appointment_system/medical_appointment_system', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/medical_appointment_system/medical_appointment_system/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('medical_appointment_system.listing', {
#             'root': '/medical_appointment_system/medical_appointment_system',
#             'objects': http.request.env['medical_appointment_system.medical_appointment_system'].search([]),
#         })

#     @http.route('/medical_appointment_system/medical_appointment_system/objects/<model("medical_appointment_system.medical_appointment_system"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('medical_appointment_system.object', {
#             'object': obj
#         })
