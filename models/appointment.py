from odoo import models, fields, api

class HospitalAppointment(models.Model):
    _name = 'hospital.appointment'
    _description = 'Hospital Appointment'

    appointment_date = fields.Datetime(string="Appointment Date", required=True, store=True)
    code = fields.Char(string="Code", required=True, copy=False, readonly=True, store=True, default='New')
    doctor_id = fields.Many2many('hospital.doctor', string="Doctors", store=True)
    patient_id = fields.Many2one('hospital.patient', string="Patient", store=True)
    stage = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
    ], string="Stage", default='draft', store=True)
    treatment_id = fields.One2many('hospital.treatment', 'appointment_id', string="Treatments")

    @api.model
    def create(self, vals):
        if vals.get('code', 'New') == 'New':
            vals['code'] = self.env['ir.sequence'].next_by_code('hospital.appointment') or 'New'
        return super(HospitalAppointment, self).create(vals)
