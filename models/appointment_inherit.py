from odoo import models, fields, api

class HospitalAppointment(models.Model):
    _inherit = 'hospital.appointment'  # inherits my appointment.py

    total_amount = fields.Char(string="Total Amount")




