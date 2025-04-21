from odoo import models, fields

class HospitalTreatment(models.Model):
    _name = 'hospital.treatment'
    _description = 'Hospital Treatment'

    name = fields.Char(string="Treatment Name", required=True)
    is_done = fields.Boolean(string="Is Done", default=False)
    appointment_id = fields.Many2one('hospital.appointment', string="Appointment")
